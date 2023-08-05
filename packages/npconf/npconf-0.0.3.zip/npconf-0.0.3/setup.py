# -*- coding: utf-8 -*-

from setuptools import setup

import npconf

# README.rst dynamically generated:
with open('README.rst', 'w') as f:
    f.write(npconf.__doc__)

NAME = 'npconf'

def read(file):
    with open(file, 'r') as f:
        return f.read().strip()

setup(
    name=NAME,
    version=read('VERSION'),
    description='A flexible, intuitive native-python configuration system.',
    long_description=read('README.rst'),
    author='Mike Burr',
    author_email='mburr@unintuitive.org',
    url='https://github.com/stnbu/{0}'.format(NAME),
    download_url='https://github.com/stnbu/{0}/archive/master.zip'.format(NAME),
    provides=[NAME],
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],
    packages=[NAME],
    keywords=['configuration'],
    test_suite='test',
)
