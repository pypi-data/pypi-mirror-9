from setuptools import setup


setup(
    name='frasco-tasks',
    version='0.1',
    url='http://github.com/frascoweb/frasco-tasks',
    license='MIT',
    author='Maxime Bouroumeau-Fuseau',
    author_email='maxime.bouroumeau@gmail.com',
    description="Celery integration for Frasco",
    py_modules=['frasco_tasks'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'frasco',
        'celery-with-redis>=3.0'
    ]
)