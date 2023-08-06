# Copyright 2011 OpenStack, LLC
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

import os
import setuptools


def read_file(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


setuptools.setup(
    name="python-keystoneclient-rackspace",
    version="0.1.3",
    author="M. David Bennett",
    author_email="mdavidbennett@syntheticworks.com",
    description="Rackspace Auth Plugin for OpenStack Clients.",
    long_description=read_file("README.md"),
    license="Apache License, Version 2.0",
    url="https://github.com/testeddoughnut/python-keystoneclient-rackspace",
    download_url=("https://github.com/testeddoughnut/"
                  "python-keystoneclient-rackspace/tarball/v0.1.3"),
    install_requires=['python-keystoneclient'],
    packages=setuptools.find_packages(exclude=['tests', 'tests.*', 'test_*']),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Environment :: OpenStack",
        "Programming Language :: Python"
    ],
    entry_points={
        "keystoneclient.auth.plugin": [
            "v2rackspace = keystoneclient_rackspace.v2_0:RackspaceAuth"
        ]
    }
)
