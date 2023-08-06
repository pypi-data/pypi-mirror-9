from setuptools import setup


setup(
    name='frasco-menu',
    version='0.1',
    url='http://github.com/frascoweb/frasco-menu',
    license='MIT',
    author='Maxime Bouroumeau-Fuseau',
    author_email='maxime.bouroumeau@gmail.com',
    description="Menu management for Frasco",
    py_modules=['frasco_menu'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'frasco'
    ]
)