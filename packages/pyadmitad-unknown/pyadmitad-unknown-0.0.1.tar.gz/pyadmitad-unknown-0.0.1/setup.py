"""The setup and build script for the pyadmitad library."""
from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

__author__ = 'trezorg@gmail.com'
__version__ = '0.0.1'

setup(
    name="pyadmitad-unknown",
    version=__version__,
    author='Igor Nemilentsev',
    author_email='trezorg@gmail.com',
    description='A Python wrapper around the Admitad API',
    license='MIT',
    url='https://github.com/trezorg/admitad-python-api.git',
    keywords='admitad',
    packages=find_packages(exclude='tests'),
    install_requires=['requests', 'simplejson'],
    test_suite='unittest2.collector',
    tests_require=['mocker', 'unittest2'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications',
        'Topic :: Internet',
    ],
)

