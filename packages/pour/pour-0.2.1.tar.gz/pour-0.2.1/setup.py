#!/usr/bin/env python

from setuptools import setup

setup(
    name='pour',
    version='0.2.1',
    url='http://www.github.com/keyanp/pour',
    license='MIT',
    author='Keyan Pishdadian',
    author_email='kpishdadian@gmail.com',
    description='A lightweight Flask app generator.',
    long_description='An ultra-lightweight command line tool to quickly '
                     'generate a bare Flask app file for prototyping.',
    install_requires=['click'],
    packages=['pour'],
    entry_points={
        'console_scripts': ['pour = pour.pour:generate']
    }

)
