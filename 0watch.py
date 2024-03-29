# Copyright (C) 2017, Bastian Eicher
# See the README file for details, or visit http://0install.net.

from __future__ import print_function

import argparse
import sys
import subprocess
from os import path
from xml.dom import minidom
from zeroinstall.injector import model

XMLNS_IFACE= 'http://zero-install.sourceforge.net/2004/injector/interface'

def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)

def load(name, path):
    if sys.version_info >= (3,):
        from importlib.machinery import SourceFileLoader
        return SourceFileLoader(name, path).load_module()
    else:
        import imp
        return imp.load_source(name, path)

parser = argparse.ArgumentParser(description='Scan a website for new releases and trigger 0template if required.')
parser.add_argument('watch_file', help='Python script that pulls a list of releases from a website')
parser.add_argument('-o', '--output', help='output directory')
args = parser.parse_args()

watch_file = path.abspath(args.watch_file)
if not watch_file.endswith('.watch.py'):
    die("Watch file must be named *.watch.py, not '{watch_file}'".format(watch_file = watch_file))
if not path.exists(watch_file):
    die("Watch file '{watch_file}' must exist".format(watch_file = watch_file))
watch_file_stem = watch_file[:-9]

template_file = watch_file_stem + '.xml.template'
if not path.exists(template_file):
    die("Template file '{template_file}' must exist".format(template_file = template_file))

output_stem = watch_file_stem if args.output is None else path.join(args.output, path.basename(watch_file_stem))
feed_file = watch_file_stem + '.xml'
def output_file(version): return output_stem + '-' + model.format_version(version) + '.xml'

watch_module = load('watch', watch_file)
releases = getattr(watch_module, 'releases', None)
if not releases:
    die("Watch file must set array of dicts 'releases'")

def already_known(version):
    if path.exists(output_file(version)): return True
    if path.exists(feed_file):
        doc = minidom.parse(feed_file)
        for elem in doc.getElementsByTagNameNS(XMLNS_IFACE, 'implementation') + doc.getElementsByTagNameNS(XMLNS_IFACE, 'group'):
            v = elem.getAttribute('version')
            if v != '' and model.parse_version(v) == version: return True
    return False

for release in releases:
    version = model.parse_version(release['version'])
    if already_known(version): continue
    retval = subprocess.call(['0template', '--output', output_file(version), template_file] + [key + '=' + value for (key, value) in release.items()])
    if retval != 0: sys.exit(retval)
