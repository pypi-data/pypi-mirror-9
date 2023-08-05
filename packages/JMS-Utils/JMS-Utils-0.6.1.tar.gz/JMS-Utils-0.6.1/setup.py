#!/usr/bin/env python

from setuptools import setup, find_packages

from jms_utils import get_version

setup(
    name='JMS-Utils',
    version=get_version(),
    description='Various utility functions',
    author='Johny Mo Swag',
    author_email='johnymoswag@gmail.com',
    url='https://github.com/JohnyMoSwag/jms-utils',
    download_url=('https://github.com/JohnyMoSwag/jms'
                  '-utils/archive/master.zip'),
    license='MIT',
    install_requires=[
        ],
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7'],
    )
