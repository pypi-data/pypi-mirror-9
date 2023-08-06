import os
from setuptools import setup
from sensorlib import __version__

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='pysensorlib',
    version=__version__,
    packages=['sensorlib'],
    install_requires = [
        "pyserial >= 2.7.0"
    ],
    author='Douglas Chambers',
    author_email='leonchambers@mit.edu',
    license='MIT',
    description='A python module for reading from sensors',
    long_description=README,
    url='https://github.com/MIT-CityFARM/pysensorlib.git',
    classifiers = [
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
