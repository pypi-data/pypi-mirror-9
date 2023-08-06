#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import glob
import types
import argparse
import logging
import ConfigParser
from flask import Flask, request, jsonify
from flaskmimerender import mimerender
from pwd import getpwnam
from grp import getgrnam
from os.path import isfile, exists, join
import yaml
import json

html_top = '''
<html>
    <head>
        <title>Peekaboo</title>
        <meta name="author" content="Michael Persson" />
        <meta name="copyright" content="Copyright (C) 2015 Michael Persson. All rights reserved." />
    </head>
    <body>
        <div id="container">
            <div id="header">
            </div>
            <div id="content">
'''

html_btm = '''
            </div>
            <div id="footer">
            </div>
        </div>
    </body>
</html>
'''

def dict_to_html(data, indent = ' ' * 4, pad = ''):
    html = '{0}<dl>\n'.format(pad)
    for key, val in data.items():
        pad2 = pad + indent
        if isinstance(val, list):
            html += '{0}<dt>{1}</dt>\n{2}<dd>\n{3}\n{4}</dd>\n'.format(pad2, key, pad2, list_to_html(val, indent, pad2 + indent), pad2)
        elif isinstance(val, dict):
            html += '{0}<dt>{1}</dt>\n{2}<dd>\n{3}\n{4}</dd>\n'.format(pad2, key, pad2, dict_to_html(val, indent, pad2 + indent), pad2)
        else:
            html += '{0}<dt>{1}</dt>\n{2}<dd>{3}</dd>\n'.format(pad2, key, pad2, val)
    html += '{0}</dl>'.format(pad)
    return html

def list_to_html(data, indent = ' ' * 4, pad = ''):
    html = '{0}<ul>\n'.format(pad)
    for val in data:
        pad2 = pad + indent
        if isinstance(val, list):
            html += '{0}<li>\n{1}\n{2}</li>\n'.format(pad2, list_to_html(val, indent, pad2 + indent), pad2)
        elif isinstance(val, dict):
            html += '{0}<li>\n{1}\n{2}</li>\n'.format(pad2, dict_to_html(val, indent, pad2 + indent), pad2)
        else:
            html += '{0}<li>{1}</li>\n'.format(pad2, val)
    html += '{0}</ul>'.format(pad)
    return html

def get_data(path):
    sys.path.insert(0, path)

    modules = {}
    for fn in glob.glob(path + '*.py'):
        fpath, fname = os.path.split(fn)
        mname, ext = os.path.splitext(fname)
        if args.debug:
            logger.info('Load module: {0}'.format(mname))
        modules[mname] = __import__(mname)

    data = {}
    for module in modules:
        for name in dir(modules[module]):
            if isinstance(modules[module].__dict__.get(name), types.FunctionType) and not name.startswith('_'):
                if args.debug:
                    logger.info('Call function: {0}.{1}'.format(module, name))
                try:
                    data.update(modules[module].__dict__.get(name)())
                except:
                    logger.warning('Function call failed {0}.{1}'.format(module, name))
                    pass
    return data

# Define arguments
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', default='/etc/peekaboo.conf', help='Configuration file')
parser.add_argument('-d', '--debug', action='store_true', help='Print debug info')
parser.add_argument('-D', '--dont-daemonize', action='store_true', help='Don''t daemonize, print result to Console')
args = parser.parse_args()

# Create formatter
formatter = logging.Formatter("[%(levelname)-8s] %(message)s")

# Create console handle
console = logging.StreamHandler()
console.setFormatter(formatter)

loglvl = logging.WARN
if args.debug:
    loglvl = logging.DEBUG

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(loglvl)
logger.addHandler(console)

# Set default configuration
config = ConfigParser.ConfigParser()
config.add_section('main')
config.set('main', 'basedir', '/var/lib/peekaboo')
config.set('main', 'user', 'peekaboo')
config.set('main', 'group', 'peekaboo')
config.add_section('http')
config.set('http', 'host', '0.0.0.0')
config.set('http', 'port', '5050')

# Get configuration
if not isfile(args.config):
    logger.critical("Configuration file doesn't exist: {0}".format(args.config))
    sys.exit(1)
config.read([args.config])

# Get user and group id
uid = getpwnam(config.get('main', 'user')).pw_uid
gid = getgrnam(config.get('main', 'group')).gr_gid

# Create base directory
basedir = config.get('main', 'basedir')
if not exists(basedir):
    makedirs(basedir)
    os.chown(basedir, uid, gid)

# If root then switch user and group
if os.getuid() == 0:
    os.setuid(uid)
if os.getgid() == 0:
    os.setgid(gid)

# Check that we're running as the correct user and group
if os.getuid() != uid:
    logger.critical('Application need to run as user: %s(%s)' % (config.get('main', 'user'), uid))
    sys.exit(1)
if os.getgid() != gid:
    logger.critical('Application need to run as group: %s(%s)' % (config.get('main', 'group'), gid))
    sys.exit(1)

app = Flask(__name__)

render_html = lambda **args: html_top + dict_to_html(args, ' ' * 4, ' ' * 16) + html_btm
render_json = lambda **args: json.dumps(args, indent = 4)
render_yaml = lambda **args: yaml.safe_dump(args)

@app.route('/info', methods=["GET"])
@mimerender(
    default = 'html',
    html = render_html,
    yaml  = render_yaml,
    json = render_json
)
def get_info():
    return get_data(join(config.get('main', 'basedir'), 'plugins/info/'))

@app.route('/status', methods=["GET"])
@mimerender(
    default = 'html',
    html = render_html,
    yaml  = render_yaml,
    json = render_json
)
def get_status():
    return get_data(join(config.get('main', 'basedir'), 'plugins/status/'))

if __name__ == '__main__':
    if args.dont_daemonize:
        print yaml.safe_dump(get_data(join(config.get('main', 'basedir'), 'plugins/info/')))
        print yaml.safe_dump(get_data(join(config.get('main', 'basedir'), 'plugins/status/')))
    elif args.debug:
        app.run(host = config.get('http', 'host'), port = config.getint('http', 'port'), debug = True)
    else:
        app.run(host = config.get('http', 'host'), port = config.getint('http', 'port'))
