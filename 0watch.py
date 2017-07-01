# Copyright (C) 2017, Bastian Eicher
# See the README file for details, or visit http://0install.net.

from __future__ import print_function

import argparse
import os
import sys
import imp
import subprocess
from xml.dom import minidom
from zeroinstall.injector import namespaces

def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)

version = '0.1'

parser = argparse.ArgumentParser(description='Scan a website for new releases and trigger 0template if required.')
parser.add_argument('watch_file', help='Python script that pulls a list of releases from a website')
parser.add_argument('-o', '--output', help='output directory')
args = parser.parse_args()

watch_file = os.path.abspath(args.watch_file)
if not watch_file.endswith('.watch.py'):
    die("Watch file must be named *.watch.py, not '{watch_file}'".format(watch_file = watch_file))
if not os.path.exists(watch_file):
    die("Watch file '{watch_file}' must exist".format(watch_file = watch_file))
watch_file_stem = watch_file[:-9]

template_file = watch_file_stem + '.xml.template'
if not os.path.exists(template_file):
    die("Template file '{template_file}' must exist".format(template_file = template_file))

feed_file_stem = watch_file_stem if args.output is None else os.path.join(args.output, os.path.basename(watch_file_stem))
feed_file = feed_file_stem + ".xml"
def versioned_feed_file(version): return feed_file_stem + '-' + version + '.xml'

watch_module = imp.load_source('watch', watch_file);
releases = getattr(watch_module, 'releases', None)
if not releases:
    die("Watch file must set array of dicts 'releases'")

def already_known(version):
    if os.path.exists(versioned_feed_file(version)): return True    
    if os.path.exists(feed_file):
        doc = minidom.parse(feed_file)
        for elem in doc.getElementsByTagNameNS(namespaces.XMLNS_IFACE, 'implementation') + doc.getElementsByTagNameNS(namespaces.XMLNS_IFACE, 'group'):
            v = elem.getAttribute('version')
            if v == version: return True
    return False

for release in releases:
    if already_known(release['version']): continue
    retval = subprocess.call(['0template', '--output', versioned_feed_file(release['version']), template_file] + [key + '=' + value for (key, value) in release.items()])
    if retval != 0: sys.exit(retval)
