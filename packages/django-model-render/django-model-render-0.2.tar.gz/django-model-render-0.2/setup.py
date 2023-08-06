#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='django-model-render',
    version='0.2',
    description='Django models extension that allows define default model templates',
    author='a1fred',
    author_email='demalf@gmail.com',
    license='MIT',
    url='https://github.com/a1fred/django-model-render',
    packages=['model_render'],
    zip_safe=False,
    install_requires = [
        'django>=1.4',
    ],
    )
