#!/usr/bin/env python
import os
from django_dropbox import version
from setuptools import setup


def get_packages():
    # setuptools can't do the job :(
    packages = []
    for root, dirnames, filenames in os.walk('django_dropbox'):
        if '__init__.py' in filenames:
            packages.append(".".join(os.path.split(root)).strip("."))

    return packages

requires = ['dropbox>=2.0.0', 'six >= 1.9.0']


setup(name='django-dropbox-redux',
    version=version,
    description='A Django App that contains a Django Storage which uses Dropbox with Python3 support.',
    author=u'Ke-Ren Dai',
    author_email='daikeren@gmail.com',
    url='https://github.com/daikeren/django-dropbox',
    packages=get_packages(),
    install_requires=requires,
)
