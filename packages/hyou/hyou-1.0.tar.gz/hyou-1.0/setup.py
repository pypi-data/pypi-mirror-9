# Copyright 2015 Google Inc. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from setuptools import setup, Extension

def read_file(name):
  with open(os.path.join(os.path.dirname(__file__), name)) as f:
    return f.read().strip()

setup(
    name='hyou',
    version='1.0',
    author='Shuhei Takahashi',
    author_email='nya@google.com',
    description='Pythonic Interface to manipulate Google Spreadsheet',
    long_description=read_file('README.txt'),
    url='https://github.com/google/hyou/',
    packages=['hyou'],
    install_requires=[
        'gdata',
        'oauth2client',
        'python-gflags',
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
