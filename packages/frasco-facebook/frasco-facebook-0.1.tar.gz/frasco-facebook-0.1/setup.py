from setuptools import setup, find_packages


setup(
    name='frasco-facebook',
    version='0.1',
    url='http://github.com/frascoweb/frasco-facebook',
    license='MIT',
    author='Maxime Bouroumeau-Fuseau',
    author_email='maxime.bouroumeau@gmail.com',
    description="Facebook integration for Frasco",
    packages=find_packages(),
    zip_safe=False,
    platforms='any',
    install_requires=[
        'frasco-users'
    ]
)