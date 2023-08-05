  
from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='perceptual',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.1',

    description='Steerable pyramid',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/andreydung/Steerable-filter',

    # Author details
    author='Dzung Nguyen',
    author_email='dzungng89@gmail.com',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[],
    download_url = 'https://github.com/andreydung/Steerable-filter/tarball/0.1',

    # What does your project relate to?
    keywords=['image processing'],

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=['perceptual'],
)