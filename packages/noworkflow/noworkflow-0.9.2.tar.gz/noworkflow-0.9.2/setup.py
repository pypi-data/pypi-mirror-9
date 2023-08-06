#!/usr/bin/env python
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop

import fnmatch
import os
import platform

from uuid import getnode


VERSION = ("0", "9", "2")


def recursive_path(pack, path):
    matches = []
    for root, dirnames, filenames in os.walk(os.path.join(pack, path)):
        for filename in filenames:
            matches.append(os.path.join(root, filename)[len(pack) + 1:])
    return matches


try:
   import pypandoc
   long_description = pypandoc.convert('../README.md', 'rst')
except (IOError, ImportError):
   long_description = (
        "Supporting infrastructure to run scientific experiments "
        "without a scientific workflow management system.")


def analytics(command_subclass):
    """Sends install statistics to analytics."""
    orig_run = command_subclass.run

    def modified_run(self):
        import sys
        try:
            try:
                from urllib2 import HTTPHandler, build_opener
                from urllib2 import urlopen, Request
                from urllib import urlencode
            except ImportError:
                from urllib.request import HTTPHandler, build_opener
                from urllib.request import urlopen, Request
                from urllib.parse import urlencode

            os_ver = platform.system()
            py_ver = '_'.join(str(x) for x in sys.version_info)
            now_ver = '_'.join(VERSION)

            code = 'os:{0},py:{1},now:{2}'.format(os_ver, py_ver, now_ver)
            action = command_subclass.action
            cid = getnode()
            payload = {
                'v': '1',
                'tid': 'UA-61791314-1',
                'cid': str(cid),
                't': 'event',
                'ec': action,
                'ea': code,
            }

            url = 'http://www.google-analytics.com/collect'
            data = urlencode(payload).encode('utf-8')
            request = Request(url, data=data)
            request.get_method = lambda: "POST"
            connection = urlopen(request)
        except:
            pass
        orig_run(self)

    command_subclass.run = modified_run
    return command_subclass


@analytics
class CustomDevelopCommand(develop):
    action = 'develop'


@analytics
class CustomInstallCommand(install):
    action = 'install'


setup(
    name = "noworkflow",
    version = '.'.join(VERSION),
    packages = find_packages(),
    package_data = {
        'noworkflow': [
            'resources/*',
        ] + recursive_path('noworkflow', 'now/vis/static')
          + recursive_path('noworkflow', 'now/vis/templates'),
    },
    entry_points = {'console_scripts': ['now = noworkflow.main:main']},
    author = ("Joao Pimentel, Leonardo Murta, Vanessa Braganholo, "
              "Fernando Chirigati, David Koop, and Juliana Freire"),
    author_email = "leomurta@ic.uff.br",
    description = "Supporting infrastructure to run scientific experiments "
                  "without a scientific workflow management system.",
    long_description = long_description,
    license = "MIT",
    keywords = "scientific experiments provenance python",
    url = "https://github.com/gems-uff/noworkflow",
    install_requires=['pyposast'],
    extras_require = {
        'vis': ['pyposast', 'flask'],
        'notebook': ['pyposast', 'ipython[notebook]'],
        'all': ['pyposast', 'ipython[notebook]', 'flask', 'pyswip-alt'],
    },
    cmdclass={
        'install': CustomInstallCommand,
        'develop': CustomDevelopCommand,
    },
)
