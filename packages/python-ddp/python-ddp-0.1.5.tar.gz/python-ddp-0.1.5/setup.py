#!/usr/bin/env python

from setuptools import setup

with open('README.md') as f:
    readme = f.read()

setup(name='python-ddp',
    version='0.1.5',
    description='An event driven ddp client',
    long_description=readme,
    license='MIT',
    author='Harrison Harnisch',
    author_email='hharnisc@gmail.com',
    url='https://github.com/hharnisc/python-ddp',
    keywords = ["meteor", "ddp", "events", "emitter", "node.js", "node", "eventemitter", "event_emitter", "ejson"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7", #only one tested
        "Topic :: Other/Nonlisted Topic"
    ],
    py_modules=['DDPClient'],
    install_requires=[
        'pyee',
        'ws4py',
        'meteor-ejson'
    ],
)