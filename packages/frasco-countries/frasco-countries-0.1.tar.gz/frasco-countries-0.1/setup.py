from setuptools import setup, find_packages


setup(
    name='frasco-countries',
    version='0.1',
    url='http://github.com/frascoweb/frasco-countries',
    license='MIT',
    author='Maxime Bouroumeau-Fuseau',
    author_email='maxime.bouroumeau@gmail.com',
    description="pycountry integration for Frasco",
    packages=find_packages(),
    zip_safe=False,
    platforms='any',
    install_requires=[
        'frasco',
        'pycountry>=1.8'
    ]
)