#
#   Copyright 2012 Bruce Yang
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import os

from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.md")).read()
CHANGES = open(os.path.join(here, "CHANGES.md")).read()

install_requires = [
    'requests',
    'click'
]

classifiers = [
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python",
    "Topic :: Software Development :: Interpreters"
]

setup(name='esqy',
      version='0.0.1',
      description='elasticsearch dsl query file runner',
      long_description="\n{0}\n\n{1}".format(README, CHANGES),
      author='Bruce Yang',
      author_email='ayang23@gmail.com',
      license='Apache-2.0',
      download_url='https://github.com/ayang/esqy/tarball/master',
      url='https://github.com/ayang/esqy',
      include_package_data=True,
      zip_safe=False,
      classifiers=classifiers,
      install_requires=install_requires,
      scripts=['esqy']
      )