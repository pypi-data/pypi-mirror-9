#!/usr/bin/env python2
from __future__ import print_function
import os, subprocess, re
from setuptools import setup, Command
from setuptools.command.sdist import sdist as _sdist
from distutils.command.build import build as _build

# The following code is taken from
# https://github.com/warner/python-ecdsa/blob/f03abf93968019758c6e00753d1b34b87fecd27e/setup.py
# which is released under the MIT license (see LICENSE for the full license
# text) and (c) 2012 Brian Warner
VERSION_PY = """
# This file is originally generated from Git information by running 'setup.py
# version'. Distribution tarballs contain a pre-generated copy of this file.

__version__ = '%s'
"""

def update_version_py():
    if not os.path.isdir(".git"):
        print("This does not appear to be a Git repository.")
        return
    try:
        p = subprocess.Popen(["git", "describe",
                              "--tags", "--dirty", "--always"],
                             stdout=subprocess.PIPE)
    except EnvironmentError:
        print("unable to run git, leaving enumerate_skip/version.py alone")
        return
    stdout = p.communicate()[0]
    if p.returncode != 0:
        print("unable to run git, leaving enumerate_skip/version.py alone")
        return
    ver = stdout.strip()
    f = open("enumerate_skip/version.py", "w")
    f.write(VERSION_PY % ver)
    f.close()
    print("set enumerate_skip/version.py to '%s'" % ver)

def get_version():
    try:
        f = open("enumerate_skip/version.py")
    except IOError as e:
        import errno
        if e.errno == errno.ENOENT:
            update_version_py()
            return get_version()
    except EnvironmentError:
        return None
    for line in f.readlines():
        mo = re.match("__version__ = '([^']+)'", line)
        if mo:
            ver = mo.group(1)
            return ver
    return None

class Version(Command):
    description = "update enumerate_skip/version.py from Git repo"
    user_options = []
    boolean_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        update_version_py()
        print("Version is now", get_version())

class sdist(_sdist):
    def run(self):
        update_version_py()
        # unless we update this, the sdist command will keep using the old
        # version
        self.distribution.metadata.version = get_version()
        return _sdist.run(self)


class build(_build):
    def run(self):
        update_version_py()
        # unless we update this, the build command will keep using the old
        # version
        self.distribution.metadata.version = get_version()
        return _build.run(self)

# Here ends the code taken from Brian Warner

setup(name="enumerate_skip",
      version=get_version(),
      author="Wieland Hoffmann",
      author_email="themineo@gmail.com",
      packages=["enumerate_skip"],
      package_dir={"enumerate_skip": "enumerate_skip"},
      download_url=["https://github.com/mineo/enumerate_skip/tarball/master"],
      url=["http://github.com/mineo/enumerate_skip"],
      license="MIT",
      classifiers=["Development Status :: 5 - Production/Stable",
                   "License :: OSI Approved :: MIT License",
                   "Natural Language :: English",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 2.6",
                   "Programming Language :: Python :: 2.7",
                   "Programming Language :: Python :: 3.2",
                   "Programming Language :: Python :: 3.3",
                   "Programming Language :: Python :: 3.4"],
      cmdclass={"version": Version, "sdist": sdist, "build": build},
      description="enumerate extended to support manual advancement or skipping\
      of the index",
      long_description=open("README.rst").read()
      )
