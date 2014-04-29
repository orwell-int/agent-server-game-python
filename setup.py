#!/usr/bin/env python

from setuptools import setup, find_packages

# Hack to prevent stupid TypeError: 'NoneType' object is not callable error on
# exit of python setup.py test # in multiprocessing/util.py _exit_function when
# running python setup.py test (see
# http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html)
try:
    import multiprocessing
    assert multiprocessing
except ImportError:
    pass

setup(
    name='orwell.agent',
    version='0.0.1',
    description='Agent connecting to the game server.',
    author='',
    author_email='',
    packages=find_packages(exclude="test"),
    test_suite='nose.collector',
    install_requires=['pyzmq'],
    tests_require=['nose', 'coverage', 'mock'],
    entry_points={
        'console_scripts': [
            'thought_police = orwell.agent.main:main',
        ]
    },
)
