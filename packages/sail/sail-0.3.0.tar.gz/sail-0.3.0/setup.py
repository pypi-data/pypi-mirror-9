#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys

from setuptools.command.install import install as _install
from setuptools import setup, find_packages

def _post_install(script_dir):
    from subprocess import call
    import platform

    if platform.system() == "Windows":
        print "Bash autompletion is not supported on windows"
        return

    if os.geteuid() != 0:
        print "Installing autocompletion for current user"
        call(['activate-global-python-argcomplete', '--user'])
    else:
        print "Installing system wide autocompletion"
        call([script_dir+'/activate-global-python-argcomplete'])

class install(_install):
    def run(self):
        _install.run(self)
        self.execute(_post_install, (self.install_scripts, ),
                     msg="Running post install task")

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "sail",
    version = "0.3.0",
    author = "Vincent Giersch, Jean-Tiare Le Bigot",
    author_email = "sail@sailabove.com",
    description = ("Sailabove CLI - Docker hosting"),
    license = "BSD",
    keywords = "cloud sailabove cli docker hosting",
    url = "http://labs.runabove.com/",
    packages = find_packages(),
    py_modules = ['__version__'],
    scripts = [
        'sail'
    ],
    install_requires = [
        'docutils>=0.3',
        'tabulate==0.7.2',
        'python-dateutil==2.2',
        'requests==2.3.0',
        'argparse==1.2.1',
        'argcomplete==0.8.1',
        'pyaml==14.05.7',
    ],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Topic :: System",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
#    cmdclass={'install': install}, # overload install command to enable postinst
)


