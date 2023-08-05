#!/usr/bin/env python

from setuptools import setup
DESCRIPTION = ("REST API framework powered by Flask, SQLAlchemy and good "
               "intentions.")

with open('README.rst') as f:
    LONG_DESCRIPTION = f.read()

install_requires = [
    'Eve>=0.5',
    'sqlalchemy>=0.8',
    'Flask-SQLAlchemy>=1.0,<2.999',
]

setup(
    name='Eve-SQLAlchemy',
    version='0.1',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author='Andrew Mleczko',
    author_email='amleczko@redturtle.it',
    url='http://github.com/redturtle/eve-sqlachemy',
    license='GPL',
    platforms=["any"],
    packages=['eve_sqlalchemy'],
    test_suite="eve_sqlalchemy.tests",
    install_requires=install_requires,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
