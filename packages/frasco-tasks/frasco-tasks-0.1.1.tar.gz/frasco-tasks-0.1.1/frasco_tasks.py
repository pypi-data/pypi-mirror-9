from frasco import Feature, action, execute_action, command, current_app, import_string, signal, copy_extra_feature_options
from celery import Celery
from celery.bin.worker import worker as celery_worker
from celery.schedules import crontab


def pack_task_args(data):
    """Traverse data and converts every object with a __taskdump__() method
    """
    if hasattr(data, "__taskdump__"):
        cls, state = data.__taskdump__()
        if not cls:
            cls = data.__class__.__module__ + "." + data.__class__.__name__
        return {"$taskobj": [cls, state]}
    if isinstance(data, (list, tuple)):
        lst = []
        for item in data:
            lst.append(pack_task_args(item))
        return lst
    if isinstance(data, dict):
        dct = {}
        for k, v in data.iteritems():
            dct[k] = pack_task_args(v)
        return dct
    return data


def unpack_task_args(data):
    """Traverse data and transforms back objects which where dumped
    using __taskdump()
    """
    if isinstance(data, (list, tuple)):
        lst = []
        for item in data:
            lst.append(unpack_task_args(item))
        return lst
    if isinstance(data, dict):
        if "$taskobj" in data:
            cls = import_string(data["$taskobj"][0])
            return cls.__taskload__(data["$taskobj"][1])
        else:
            dct = {}
            for k, v in data.iteritems():
                dct[k] = unpack_task_args(v)
            return dct
    return data


def run_action(name, **kwargs):
    """Instanciates and executes an action from current_app.
    This is the actual function which will be queued.
    """
    kwargs = unpack_task_args(kwargs)
    current_user = None
    if '_current_user' in kwargs:
        current_user = kwargs.pop('_current_user')
        current_app.features.users.start_user_context(current_user)
    try:
        current_app.features.tasks.before_task_event.send(name=name)
        action = current_app.actions[name](kwargs)
        rv = execute_action(action)
        current_app.features.tasks.after_task_event.send(name=name)
    finally:
        if current_user:
            current_app.features.users.stop_user_context()
    return rv


class TasksFeature(Feature):
    """Enqueue tasks to process them in the background
    """
    name = "tasks"
    command_group = False
    defaults = {"broker_url": None,
                "result_backend": None,
                "accept_content": ['json', 'msgpack', 'yaml'],
                "task_serializer": "json",
                "schedule": {}}

    before_task_event = signal("before_task")
    after_task_event = signal("after_task")
    task_enqueued_event = signal("task_enqueued")

    def init_app(self, app):
        broker = self.options["broker_url"]
        backend = self.options["result_backend"]
        if not broker:
            if app.features.exists("redis"):
                broker = app.features.redis.options["url"]
            else:
                broker = "redis://localhost"
            if not backend:
                backend = broker
        self.celery = Celery(__name__, broker=broker, backend=backend)
        self.celery.conf["CELERY_ACCEPT_CONTENT"] = self.options["accept_content"]
        self.celery.conf["CELERY_TASK_SERIALIZER"] = self.options["task_serializer"]
        self.celery.conf["CELERYBEAT_SCHEDULE_FILENAME"] = ".celerybeat-schedule"
        copy_extra_feature_options(self, self.celery.conf, "CELERY_")

        self.celery.conf["CELERYBEAT_SCHEDULE"] = {}
        if self.options["schedule"]:
            for action, schedule in self.options["schedule"].iteritems():
                self.schedule_action(action, schedule)

        self.celery.task(name="frasco_run_action")(run_action)
        app.processes.append(("worker", ["frasco", "worker"]))

    def add_task(self, func, **kwargs):
        return self.celery.task(**kwargs)(func)

    def send_task(self, *args, **kwargs):
        return self.celery.send_task(*args, **kwargs)

    def schedule_task(self, schedule_name, name, schedule, **kwargs):
        if isinstance(schedule, dict):
            schedule = crontab(**schedule)
        elif isinstance(schedule, str):
            schedule = crontab(*schedule.split(" "))
        self.celery.conf["CELERYBEAT_SCHEDULE"][schedule_name] = dict(
            task=name, schedule=schedule, **kwargs)

    def schedule_action(self, action, schedule, name=None):
        if not name:
            name = "scheduled_%s" % action
        self.schedule_task(name, "frasco_run_action", schedule,
            args=(action,))

    @action(default_option="action")
    def enqueue(self, action, **kwargs):
        if current_app.features.exists('users') and current_app.features.users.logged_in():
            kwargs.setdefault('_current_user', current_app.features.users.current)
        result = self.celery.send_task("frasco_run_action", (action,), pack_task_args(kwargs))
        self.task_enqueued_event.send(self, action=action, result=result)
        return result

    @command(with_reloader=True)
    def worker(self):
        current_app.logger.handlers = [] # celery provides handlers
        beat = True if self.celery.conf["CELERYBEAT_SCHEDULE"] else False
        w = celery_worker(self.celery)
        w.run(beat=beat)