#!/usr/bin/env python

# COPYRIGHT 2014 Pluribus Networks Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import setuptools

setuptools.setup(
    author='Pluribus Networks',
    author_email='openstack@pluribusnetworks.com',
    description='OpenStack Neutron Pluribus plugin',
    license='Apache License, Version 2.0',
    long_description=open("README.rst").read(),
    name='neutron-plugin-pluribus',
    packages=setuptools.find_packages(
        exclude=['*.tests','*.tests.*','tests.*','tests']),
    url='http://www.pluribusnetworks.com',
    version='3.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        ],
)
