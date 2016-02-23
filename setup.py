#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='lifeboat',
    version='0.1',
    description='Lifeboat',
    author='Steven Manning',
    author_email='manning@tamu.edu',
    install_requires=['django==1.8', 'markdown', 'MySQL-python',
       'celery', 'django-celery', 'django-filter', 'djangorestframework==3.2.4', ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
