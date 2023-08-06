# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='django-commentator',
    version='0.0.3',
    description='Commentaries system for Django',
    long_description=open('README.rst').read(),

    author='Alex Vakhitov',
    author_email='alex.vakhitov@gmail.com',
    license="MIT",
    url='https://github.com/smidth/django-commentator',

    packages=['commentator'],
    include_package_data=True,
    install_requires=['Django', 'setuptools'],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
)
