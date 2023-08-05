#!/usr/bin/python
"""
Package configuration for confset module and utility
"""
from distutils.core import setup
#noinspection PyStatementEffect
"""
 Copyright (c) 2012-2014 Dwight Hubbard. All rights reserved.
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License. See accompanying LICENSE file.
"""

setup(
    name="confset",
    version="0.0.34",
    author="Dwight Hubbard",
    author_email="d@d-h.us",
    url="http://computing.dwighthubbard.info",
    license="LICENSE.txt",
    packages=["confset"],
    scripts=['bin/confset'],
    long_description=open('README.md').read(),
    description="A simple script to change or update package configurations",
    requires=['configobj'],
)
