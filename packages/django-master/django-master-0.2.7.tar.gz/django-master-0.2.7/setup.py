# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-master',
    version=open('djangomaster/version.txt').read().strip(),
    author=u'Andre Farzat',
    author_email='andrefarzat@gmail.com',
    packages=find_packages(),
    url='http://github.com/django-master/django-master',
    license='LICENSE',
    description='django master dashboard',
    long_description=open('README.md').read(),
    install_requires=open('requirements.txt').readlines(),
    include_package_data=True,
    zip_safe=False,
)
