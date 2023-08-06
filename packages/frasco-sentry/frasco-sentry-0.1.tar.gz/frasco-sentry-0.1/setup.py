from setuptools import setup


setup(
    name='frasco-sentry',
    version='0.1',
    url='http://github.com/frascoweb/frasco-sentry',
    license='MIT',
    author='Maxime Bouroumeau-Fuseau',
    author_email='maxime.bouroumeau@gmail.com',
    description="Sentry integration for Frasco",
    py_modules=['frasco_sentry'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'frasco',
        'raven>=5.0.0'
    ]
)