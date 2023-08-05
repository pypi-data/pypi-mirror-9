#! /usr/bin/env python
# -*- coding: utf-8 -*-


# Biryani -- A conversion and validation toolbox
# By: Emmanuel Raviart <emmanuel@raviart.com>
#
# Copyright (C) 2009, 2010, 2011, 2012, 2013, 2014, 2015 Emmanuel Raviart
# http://packages.python.org/Biryani/
#
# This file is part of Biryani.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Toolbox to convert and validate data (for web forms, CSV files, XML files,
etc)"""


from setuptools import setup, find_packages


classifiers = """\
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: Apache Software License
Operating System :: OS Independent
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
Topic :: Text Processing
"""

doc_lines = __doc__.split('\n')


setup(
    name='Biryani',
    version='0.10.4',

    author='Emmanuel Raviart',
    author_email='emmanuel@raviart.com',
    classifiers=[classifier for classifier in classifiers.split('\n')
                 if classifier],
    description=doc_lines[0],
    keywords='conversion form python validation web',
    license='http://www.apache.org/licenses/LICENSE-2.0',
    long_description='\n'.join(doc_lines[2:]),
    url='http://biryani.readthedocs.org/',

    extras_require=dict(
        bsonconv=['pymongo'],
        datetimeconv=['isodate >= 0.4', 'pytz'],
        dev=['flake8', 'sphinx', 'Sphinx-PyPI-upload'],
        jwtconv=['pycrypto'],
        netconv=['pydns'],
        webobconv=['webob'],
        ),
    include_package_data=True,
    install_requires=['Babel >= 0.9.4'],
    message_extractors={
        'biryani': [('**.py', 'python', None)],
        },
    packages=find_packages(),
    zip_safe=False,
    )
