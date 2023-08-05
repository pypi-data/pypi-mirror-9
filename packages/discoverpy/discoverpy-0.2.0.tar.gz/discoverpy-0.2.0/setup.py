"""Setuptools configuration for discoverpy."""

from setuptools import setup
from setuptools import find_packages


with open('README.rst', 'r') as readmefile:

    README = readmefile.read()

with open('requirements.txt', 'r') as reqfile:

    REQUIREMENTS = reqfile.readlines()

setup(
    name='discoverpy',
    version='0.2.0',
    url='https://github.com/kevinconway/discover.py',
    description='REST framework for discoverable services.',
    author="Kevin Conway",
    author_email="kevinjacobconway@gmail.com",
    long_description=README,
    license='MIT',
    packages=find_packages(exclude=['tests', 'build', 'dist', 'docs']),
    requires=REQUIREMENTS,
    entry_points={
        'console_scripts': [

        ],
    },
    include_package_data=True,
)
