#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='hashable',
    version='0.1',
    description='Allow objects to be hashable and comparable by attributes',
    author='Karataev Pavel',
    author_email='karataev.pavel@gmail.com',
    url='https://github.com/minmax/hashable',
    license='MIT',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
