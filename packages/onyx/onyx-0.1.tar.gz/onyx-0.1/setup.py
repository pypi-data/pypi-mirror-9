###############################################################################
#
#   Onyx Portfolio & Risk Management Framework
#
#   Copyright 2014 Carlo Sbraccia
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
###############################################################################

# FIXME: distutils problem with hardlinks
import os
del os.link

from setuptools import setup, find_packages

install_requires = [
    "dateutils",
    "numpy",
    "pylru",
    "psycopg2",
]

setup(
    name="onyx",
    setup_requires=["hgtools"],
    use_vcs_version={"increment": "0.1"},
    description="A framework to create portfolio and risk management systems",
    author="carlo sbraccia",
    author_email="carlo.sbraccia@yahoo.co.uk",
    url="https://bitbucket.org/sbraccia/onyx",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
)
