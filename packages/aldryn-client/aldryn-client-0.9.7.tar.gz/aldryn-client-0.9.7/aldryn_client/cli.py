# -*- coding: utf-8 -*-
import docopt
import imp
import platform
import os
import sys

from . import __version__ as version
from .client import Client
from .utils import cli_confirm

try:
    imp.find_module('kivy')
except ImportError:
    GUI = False
else:
    GUI = True

doc_draft = """django CMS cloud client.

Usage:%(extra_commands)s
    aldryn login [--with-token]
    aldryn boilerplate upload
    aldryn boilerplate validate
    aldryn addon upload
    aldryn addon validate
    aldryn sync [--sitename=<sitename>]
    aldryn workspace create --sitename=<sitename> [--path=<sitename>]
    aldryn sites
    aldryn newest_version

Options:
    -h --help                   Show this screen.
    --version                   Show version.
    --sitename=<sitename>       Domain of your site, eg example.cloud.django-cms.com.
"""

gui_command = """
    aldryn gui"""

if GUI:
    __doc__ = doc_draft % {'extra_commands': gui_command}
else:
    __doc__ = doc_draft % {'extra_commands': ''}


def _network_error_callback(message, on_confirm, on_cancel):
    question = 'Retry syncing the file?'
    if cli_confirm(question, message=message, default=True):
        on_confirm()
    else:
        on_cancel()


def _protected_file_change_callback(message):
    print '!!!'
    print message
    print '!!!'


def _sync_error_callback(message, title=None):
    if title:
        print title
    print message


def main():
    args = docopt.docopt(__doc__, version=version)
    client = Client(Client.get_host_url(), interactive=True)
    retval = True
    msg = None
    if GUI and args['gui']:
        from main import AldrynGUIApp
        AldrynGUIApp().run()
    elif args['login']:
        if args['--with-token']:
            retval, msg = client.login_with_token()
        else:
            retval, msg = client.login()
    elif args['boilerplate']:
        if args['upload']:
            retval, msg = client.upload_boilerplate()
        elif args['validate']:
            retval, msg = client.validate_boilerplate()
    elif args['addon']:
        if args['upload']:
            retval, msg = client.upload_app()
        elif args['validate']:
            retval, msg = client.validate_app()
    elif args['sync']:
        retval, msg = client.sync(
            _network_error_callback,
            _sync_error_callback,
            _protected_file_change_callback,
            sitename=args.get('--sitename', None))
    elif args['sites']:
        retval, msg = client.sites()
    elif args['newest_version']:
        print 'Current version: %s' % version
        retval, version_data = client.newest_version()
        if retval:
            if version_data:
                newest_version = version_data['version']
            else:
                newest_version = None
            if newest_version and newest_version > version:
                system = platform.system()
                if True or system == 'Darwin':
                    link = version_data['osx_link']
                elif system == 'Windows':
                    link = version_data['windows_link']
                elif system == 'Linux':
                    if platform.architecture().startswith('32'):
                        link = version_data['linux32_link']
                    else:
                        link = version_data['linux64_link']
                else:
                    link = None
                if link:
                    msg = 'You can download the newest version (%s) from here:\n%s' % (
                        newest_version, link)
                else:
                    msg = 'Newer version is available (%s).' % newest_version
            else:
                msg = 'You are using the latest version.'
    elif args['workspace']:
        if args['create']:
            retval, msg = client.create_workspace(
                sitename=args.get('--sitename', None),
                path=args.get('--path', None),
            )
    if msg:
        print msg
    sys.exit(int(retval))
