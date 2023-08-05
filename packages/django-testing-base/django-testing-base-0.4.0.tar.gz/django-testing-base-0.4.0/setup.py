#!/usr/bin/env python
import os
from setuptools import setup, find_packages


os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))
with open('README.rst') as f:
    README = f.read()
with open('pip_requirements.txt') as f:
    REQUIREMENTS = f.readlines()

setup(
    name='django-testing-base',
    version='0.4.0',
    packages=find_packages(exclude=['testsite']),
    include_package_data=True,
    install_requires=REQUIREMENTS,
    license='MIT License',
    description='Simple Django testing base classes and patterns',
    long_description=README,
    url='https://github.com/tctimmeh/django-testing-base',
    author='Tim Court',
    author_email='tctimmeh@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
