# -*- coding: utf-8 -*-
import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='lxml-xpath2-functions',
    version='0.0.4',
    packages=['xpath2_functions'],
    include_package_data=True,
    license='LGPL',
    description='Set of Xpath 2.0 functions which you can register in lxml',
    long_description=README,
    url='https://bitbucket.org/kkujawinski/lxml-xpath2-functions',
    author='Kamil Kujawinski',
    author_email='kamil@kujawinski.net',
    install_requires=[
        'lxml',
    ],
    tests_require=[
        'unittest2',
    ],
    test_suite="tests",
    classifiers=[
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet',
        'Topic :: Software Development :: Testing',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
