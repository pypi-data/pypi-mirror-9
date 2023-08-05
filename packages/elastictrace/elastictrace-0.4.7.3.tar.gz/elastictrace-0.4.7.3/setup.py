#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='elastictrace',
    version='0.4.7.3',
    description='elasticTrace Agent for getting server metrics upstream',
    author='elasticTrace.com',
    author_email='hello@elastictrace.com',
    url='http://elastictrace.com/',
    packages=find_packages(),
    install_requires=['requests', 'psutil'],
    zip_safe = False,
    entry_points={
        'console_scripts': [
            'elastictrace-agent = elastictrace.agent:main'
        ]
    }
)
