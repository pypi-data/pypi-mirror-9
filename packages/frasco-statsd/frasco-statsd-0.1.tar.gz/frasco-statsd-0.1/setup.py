from setuptools import setup


setup(
    name='frasco-statsd',
    version='0.1',
    url='http://github.com/frascoweb/frasco-statsd',
    license='MIT',
    author='Maxime Bouroumeau-Fuseau',
    author_email='maxime.bouroumeau@gmail.com',
    description="Statsd integration for Frasco",
    py_modules=['frasco_statsd'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'frasco',
        'statsd'
    ]
)