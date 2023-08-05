# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

version = __import__('djleetchi').__version__

root = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(root, 'README.rst')) as f:
    README = f.read()

setup(
    name='django-leetchi',
    version=version,
    description='An integration of python-leetchi with Django framework',
    long_description=README,
    author='Florent Messa',
    author_email='florent.messa@gmail.com',
    url='http://github.com/thoas/django-leetchi',
    packages=find_packages(),
    install_requires=[
        'python-leetchi>=0.3.5',
        'six',
        'django-iban==0.2.5',
        'python-dateutil',
    ],
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ]
)
