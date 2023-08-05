#!/usr/bin/env python
import os
from pathlib import Path
from setuptools import setup, find_packages


os.chdir(str(Path(__file__).parent))
with open('README.rst') as f:
    README = f.read()
with open('pip_requirements.txt') as f:
    REQUIREMENTS = f.readlines()

setup(
    name='dc-django-base',
    version='0.3.2',
    packages=find_packages(include=['dcbase*']),
    include_package_data=True,
    install_requires=REQUIREMENTS,
    license='MIT License',
    description='Django base application',
    long_description=README,
    url='https://github.com/tctimmeh/dc-django-base',
    author='Tim Court',
    author_email='tctimmeh@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
)
