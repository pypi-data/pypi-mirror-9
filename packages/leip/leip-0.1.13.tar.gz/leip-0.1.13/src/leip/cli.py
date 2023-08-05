# -*- coding: utf-8 -*-
from __future__ import print_function,  unicode_literals

import logging
import os
import sys

import leip

def dispatch():
    """
    Run the app - this is the actual entry point
    """
    app.run()

CLI_TEMPLATE = '''
import leip

def dispatch():
    """
    Run the {name} app
    """
    app.run()


app = leip.app(name='{name}')
app.discover(globals())
'''

HELLO_WORLD_PLUGIN_TEMPLATE = '''
import leip

@leip.arg('name', help='Say hello to')
@leip.command
def hello_world(app, args):
    print "{{}} {{}}".format(app.conf['message'], args.name)
'''

CONF_TEMPLATE = """message: Kia ora
"""

PLUGIN_CONF_TEMPLATE = """hello_world:
  module: {name}.plugin.hello_world
  enabled: true
"""

README_TEMPLATE = """
The great '{project}' project
=============================

Author: {author} <{email}>

Documentation follows (or so I hope).
"""

SETUP_PY_TEMPLATE = """#!/usr/bin/env python

from setuptools import setup, find_packages

#one line description
with open('DESCRIPTION') as F:
    description = F.read().strip()

#version number
with open('VERSION') as F:
    version = F.read().strip()

entry_points = {{
    'console_scripts': [
        '{name} = {name}.cli:dispatch'
        ]}}

setup(name='{name}',
      version=version,
      description=description,
      author='{author}',
      author_email='{email}',
      entry_points = entry_points,
      include_package_data=True,
      url='https://encrypted.google.com/#q={name}&safe=off',
      packages=find_packages(),
      install_requires=[
                'Leip',
                ],
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        ]
     )
"""

def create_file(pth, content):
    bn = os.path.dirname(pth)
    print(bn)
    if not os.path.exists(bn):
        print(bn)
        os.makedirs(bn)
    if not os.path.exists(pth):
        with open(pth, 'w') as F:
            F.write(content)

@leip.arg('email', help='author email')
@leip.arg('author', help='author name')
@leip.arg('name', help='project name')
@leip.command
def create(app, args):
    """
    Create a new, empty, project in the current directory
    """

    tdata = vars(args)
    name = args.name
    project = name.capitalize()
    tdata['project'] = project

    src = os.path.join(project, name.lower())
    if not os.path.exists(src):
        os.makedirs(src)

    etc = os.path.join(project, name.lower(), 'etc')
    if not os.path.exists(etc):
        os.makedirs(etc)

    initpy = os.path.join(src, '__init__.py')
    create_file(initpy, "")

    readme = os.path.join(project, 'README')
    create_file(readme, README_TEMPLATE.format(**tdata))

    conf = os.path.join(src, 'etc', '_{}.config'.format(name))
    create_file(conf, CONF_TEMPLATE)

    p_conf = os.path.join(src, 'etc', 'plugin.config'.format(name))
    create_file(p_conf, PLUGIN_CONF_TEMPLATE.format(**tdata))

    setup_py = os.path.join(project, 'setup.py')
    create_file(setup_py, SETUP_PY_TEMPLATE.format(**tdata))

    cli_py = os.path.join(src, 'cli.py')
    create_file(cli_py, CLI_TEMPLATE.format(**tdata))

    hw_py = os.path.join(src, 'plugin', 'hello_world.py')
    create_file(hw_py, HELLO_WORLD_PLUGIN_TEMPLATE.format(**tdata))

    hwi_py = os.path.join(src, 'plugin', '__init__.py')
    create_file(hwi_py, "")

    create_file(os.path.join(project, 'MANIFEST.in'),
        "recursive-include {name}/etc *.config\n".format(**tdata))

    create_file(os.path.join(project, 'DESCRIPTION'),
        "One line description of {project}".format(**tdata))

    create_file(os.path.join(project, 'VERSION'),
        "0.0.1")

#    os.makedirs(os.path.join(name))

app = leip.app(name='leip', set_name=None)
app.discover(globals())
