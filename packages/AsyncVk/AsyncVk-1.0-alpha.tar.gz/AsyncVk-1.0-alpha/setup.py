#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='AsyncVk',
    version='1.0-alpha',

    author='Ivan Tsyganov',
    author_email='tsyganov.ivan@gmail.com',

    url='https://github.com/tsyganov-ivan/AsyncVk',
    description='vk.com API async Python wrapper. Only Python 3.4+',

    packages=find_packages(),
    install_requires='requests',

    license='MIT License',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='vk.com asyncio async api vk vkontakte wrappper',
)
