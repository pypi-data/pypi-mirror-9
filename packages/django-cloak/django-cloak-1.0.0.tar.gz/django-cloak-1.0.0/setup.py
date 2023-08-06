#!/usr/bin/env python
import sys
from setuptools import setup

django_version = "django"
if sys.version_info[0] < 3:
    django_version += "<1.7"

setup(
    name="django-cloak",
    version="1.0.0",
    url='https://github.com/PSU-OIT-ARC/django-cloak',
    author='Matt Johnson',
    author_email='mdj2@pdx.edu',
    description="App for Django to cloak as a user, or generate a login link",
    packages=['cloak','cloak.management', 'cloak.management.commands'],
    zip_safe=False,
    classifiers=[
        'Framework :: Django',
    ],
    extras_require={
        'test': ['model_mommy', 'mock', django_version],
    }
)
