#!/usr/bin/env python

# pywws - Python software for USB Wireless Weather Stations
# http://github.com/jim-easterbrook/pywws
# Copyright (C) 2008-14  Jim Easterbrook  jim@jim-easterbrook.me.uk

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from __future__ import with_statement

from datetime import date
from distutils.command.upload import upload
import os
from setuptools import setup
import sys

# read current version info without importing pywws package
if sys.version_info[0] >= 3:
    with open('src/pywws/__init__.py') as f:
        exec(f.read())
else:
    execfile('src/pywws/__init__.py')

# get GitHub repo information
# requires GitPython - 'sudo pip install gitpython --pre'
last_commit = _commit
last_release = None
try:
    import git
    try:
        repo = git.Repo()
        latest = 0
        for tag in repo.tags:
            if tag.tag.tagged_date > latest:
                latest = tag.tag.tagged_date
                last_release = str(tag)
        last_commit = str(repo.head.commit)[:7]
    except git.exc.InvalidGitRepositoryError:
        pass
except ImportError:
    pass

# regenerate version info, if required
if last_commit != _commit:
    _release = str(int(_release) + 1)
    _commit = last_commit
if last_release:
    major, minor, patch = last_release.split('.')
    today = date.today()
    if today.strftime('%m') == minor:
        patch = int(patch) + 1
    else:
        patch = 0
    next_release = today.strftime('%y.%m') + '.%d' % patch
    version = next_release + '.dev%s' % _release
else:
    next_release = '.'.join(__version__.split('.')[:3])
    version = next_release

if version != __version__:
    vf = open('src/pywws/__init__.py', 'w')
    vf.write("""__version__ = '%s'
_release = '%s'
_commit = '%s'
""" % (version, _release, _commit))
    vf.close()

cmdclass = {}
command_options = {}

if 'LANG' in os.environ:
    lang = os.environ['LANG'].split('_')[0]
else:
    lang = 'en'

# add commands to create & build translation files
# requires Babel to be installed
command_options['compile_catalog'] = {
    'domain'    : ('setup.py', 'pywws'),
    'directory' : ('setup.py', 'src/pywws/lang'),
    'use_fuzzy' : ('setup.py', '1'),
    }
command_options['extract_messages'] = {
    'input_dirs'         : ('setup.py', 'src/pywws'),
    'output_file'        : ('setup.py', 'build/gettext/pywws.pot'),
    'no_wrap'            : ('setup.py', '1'),
    'sort_by_file'       : ('setup.py', '1'),
    'add_comments'       : ('setup.py', 'TX_NOTE'),
    'strip_comments'     : ('setup.py', '1'),
    'copyright_holder'   : ('setup.py', 'Jim Easterbrook'),
    'msgid_bugs_address' : ('setup.py', 'jim@jim-easterbrook.me.uk'),
    }
command_options['init_catalog'] = {
    'domain'     : ('setup.py', 'pywws'),
    'input_file' : ('setup.py', 'build/gettext/pywws.pot'),
    'output_dir' : ('setup.py', 'src/pywws/lang'),
    'no_wrap'    : ('setup.py', '1'),
    }
command_options['update_catalog'] = {
    'domain'     : ('setup.py', 'pywws'),
    'input_file' : ('setup.py', 'build/gettext/pywws.pot'),
    'output_dir' : ('setup.py', 'src/pywws/lang'),
    'no_wrap'    : ('setup.py', '1'),
    }

# if sphinx is installed, add commands to build documentation
try:
    from sphinx.setup_command import BuildDoc
    # compile documentation to html
    cmdclass['build_sphinx'] = BuildDoc
    command_options['build_sphinx'] = {
        'source_dir' : ('setup.py', 'src/doc'),
        'build_dir'  : ('setup.py', 'doc/%s' % (lang)),
        'builder'    : ('setup.py', 'html'),
        }
    # extract strings for translation
    class extract_messages_doc(BuildDoc):
        description = 'extract localizable strings from the documentation'
    cmdclass['extract_messages_doc'] = extract_messages_doc
    command_options['extract_messages_doc'] = {
        'source_dir' : ('setup.py', 'src/doc'),
        'build_dir'  : ('setup.py', 'build'),
        'builder'    : ('setup.py', 'gettext'),
        }
except ImportError:
    pass

# set options for uploading documentation to PyPI
command_options['upload_docs'] = {
    'upload_dir' : ('setup.py', 'doc'),
    }

# modify upload class to add appropriate tag
# requires GitPython - 'sudo pip install gitpython --pre'
class upload_and_tag(upload):
    def run(self):
        import git
        message = ''
        with open('CHANGELOG.txt') as cl:
            while not cl.readline().startswith('Changes'):
                pass
            while True:
                line = cl.readline().strip()
                if not line:
                    break
                message += line + '\n'
        repo = git.Repo()
        tag = repo.create_tag(next_release, message=message)
        remote = repo.remotes.origin
        remote.push(tags=True)
        return upload.run(self)
cmdclass['upload'] = upload_and_tag

# set options for building distributions
command_options['sdist'] = {
    'formats'        : ('setup.py', 'gztar zip'),
    }

with open('README.rst') as ldf:
    long_description = ldf.read()

setup(name = 'pywws',
      version = next_release,
      description = 'Python software for wireless weather stations',
      author = 'Jim Easterbrook',
      author_email = 'jim@jim-easterbrook.me.uk',
      url = 'http://jim-easterbrook.github.com/pywws/',
      download_url = 'https://pypi.python.org/pypi/pywws/%s' % next_release,
      long_description = long_description,
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: End Users/Desktop',
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          ],
      license = 'GNU GPL',
      platforms = ['POSIX', 'MacOS', 'Windows'],
      packages = ['pywws'],
      package_dir = {'' : 'src'},
      package_data = {
          'pywws' : [
              'services/*',
              'lang/*/LC_MESSAGES/pywws.mo',
              'examples/*/*.*', 'examples/*/*/*.*',
              ],
          },
      cmdclass = cmdclass,
      command_options = command_options,
      entry_points = {
          'console_scripts' : [
              'pywws-hourly             = pywws.Hourly:main',
              'pywws-livelog            = pywws.LiveLog:main',
              'pywws-livelog-daemon     = pywws.livelogdaemon:main',
              'pywws-reprocess          = pywws.Reprocess:main',
              'pywws-setweatherstation  = pywws.SetWeatherStation:main',
              'pywws-testweatherstation = pywws.TestWeatherStation:main',
              'pywws-version            = pywws.version:main',
              ],
          },
      extras_require = {
          'daemon'  : ['python-daemon'],
          'sftp'    : ['paramiko', 'pycrypto'],
          'twitter' : ['python-twitter >= 1.0', 'oauth2'],
          },
      zip_safe = False,
      use_2to3 = True,
      )
