from setuptools import setup


setup(
    name='frasco-search',
    version='0.1',
    url='http://github.com/frascoweb/frasco-search',
    license='MIT',
    author='Maxime Bouroumeau-Fuseau',
    author_email='maxime.bouroumeau@gmail.com',
    description="Elastisearch integration for Frasco",
    py_modules=['frasco_search'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'frasco',
        'elasticsearch>=1.2.0'
    ]
)