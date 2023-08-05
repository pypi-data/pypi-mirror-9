# -*- coding: utf-8 -*-
##
# Copyright (c) 2006-2015 Apple Inc. All rights reserved.
# Copyright (c) 2015 Norman Krämer. All rights reserved.
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
##

from setuptools import setup
from distutils.core import setup, Extension
import subprocess

def getoutput(cmd_and_args):
    process = subprocess.Popen(cmd_and_args, stdout=subprocess.PIPE, universal_newlines=True)
    out, err = process.communicate()
    retcode = process.poll()
    if retcode:
        raise subprocess.CalledProcessError(retcode, cmd_and_args[0], output=out)
    return out

long_description = """
This is a small modification to the PyKerberos project making it usable with python3/python2.
The original source is at http://trac.calendarserver.org/browser/PyKerberos/trunk?rev=14295.

This Python package is a high-level wrapper for Kerberos (GSSAPI) operations.
The goal is to avoid having to build a module that wraps the entire Kerberos.framework,
and instead offer a limited set of functions that do what is needed for client/server
Kerberos authentication based on <http://www.ietf.org/rfc/rfc4559.txt>.

"""

sources = ["src/base64.c", "src/kerberosbasic.c", "src/kerberosgss.c", "src/kerberospw.c", "src/kerberos-py23.c"]

link_args = getoutput("krb5-config --libs gssapi".split()).split()
compile_args = getoutput("krb5-config --cflags gssapi".split()).split()

#compile_args.append("-Werror=missing-declarations")
#compile_args.append("-Werror=implicit-function-declaration")

setup (
    name = "kerberos-py23",
    # use the version from the PyKerberos project plus an additional nano-version that is used to track changes to this kerberos-py23 packages
    url="https://github.com/may-day/kerberos-py23",
    version = "1.1.1.0",
    description = "Kerberos high-level interface",
    long_description=long_description,
    license='Apache Software License 2.0',
    classifiers = [
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration :: Authentication/Directory"
        ],
    ext_modules = [
        Extension(
            "kerberos",
            extra_link_args = link_args,
            extra_compile_args = compile_args,
            sources = sources
        ),
    ],
)
