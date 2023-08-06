from setuptools import setup


setup(
    name='frasco-geoip',
    version='0.1',
    url='http://github.com/frascoweb/frasco-geoip',
    license='MIT',
    author='Maxime Bouroumeau-Fuseau',
    author_email='maxime.bouroumeau@gmail.com',
    description="pygeoip integration for Frasco",
    py_modules=["frasco_geoip"],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'frasco',
        'pygeoip>=0.3.1'
    ]
)