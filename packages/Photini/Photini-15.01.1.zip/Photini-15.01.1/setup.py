#!/usr/bin/env python
#  Photini - a simple photo metadata editor.
#  http://github.com/jim-easterbrook/Photini
#  Copyright (C) 2012-15  Jim Easterbrook  jim@jim-easterbrook.me.uk
#
#  This program is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see
#  <http://www.gnu.org/licenses/>.

from datetime import date
from distutils.cmd import Command
from distutils.command.upload import upload
from distutils.errors import DistutilsOptionError
import os
from setuptools import setup
from setuptools.command.install import install as _install
import subprocess
import sys

# read current version info without importing package
with open('src/photini/__init__.py') as f:
    exec(f.read())

cmdclass = {}
command_options = {}

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
            tag_name = str(tag)
            if (tag_name.startswith('Photini') and
                    tag.commit.committed_date > latest):
                latest = tag.commit.committed_date
                last_release = tag_name
        last_commit = str(repo.head.commit)[:7]
    except git.exc.InvalidGitRepositoryError:
        pass
except ImportError:
    pass

# regenerate version file, if required
if last_commit != _commit:
    _dev_no = str(int(_dev_no) + 1)
    _commit = last_commit
if last_release:
    major, minor, patch = last_release.split('.')
    today = date.today()
    if today.strftime('%m') == minor:
        patch = int(patch) + 1
    else:
        patch = 0
    next_release = today.strftime('%y.%m') + '.%d' % patch
    next_version = next_release + '.dev%s' % _dev_no
else:
    next_release = '.'.join(__version__.split('.')[:3])
    next_version = next_release
if next_version != __version__:
    with open('src/photini/__init__.py', 'w') as vf:
        vf.write("from __future__ import unicode_literals\n\n")
        vf.write("__version__ = '%s'\n" % next_version)
        vf.write("_dev_no = '%s'\n" % _dev_no)
        vf.write("_commit = '%s'\n" % _commit)

# if sphinx is installed, add command to build documentation
try:
    from sphinx.setup_command import BuildDoc
    cmdclass['build_sphinx'] = BuildDoc
    command_options['build_sphinx'] = {
        'all_files'  : ('setup.py', '1'),
        'source_dir' : ('setup.py', 'src/doc'),
        'build_dir'  : ('setup.py', 'doc'),
        'builder'    : ('setup.py', 'html'),
        }
except ImportError:
    pass

# set options for uploading documentation to PyPI
command_options['upload_docs'] = {
    'upload_dir' : ('setup.py', 'doc/html'),
    }

# modify upload class to add appropriate tag
# requires GitPython - 'sudo pip install gitpython --pre'
class upload_and_tag(upload):
    def run(self):
        import git
        tag_path = 'Photini-%s' % next_release
        message = '%s\n\n' % tag_path
        with open('CHANGELOG.txt') as cl:
            while not cl.readline().startswith('Changes'):
                pass
            while True:
                line = cl.readline().strip()
                if not line:
                    break
                message += line + '\n'
        repo = git.Repo()
        tag = repo.create_tag(tag_path, message=message)
        remote = repo.remotes.origin
        remote.push(tags=True)
        return upload.run(self)
cmdclass['upload'] = upload_and_tag

# set options for building distributions
command_options['sdist'] = {
    'formats'        : ('setup.py', 'gztar zip'),
    'force_manifest' : ('setup.py', '1'),
    }

# extend install command to add menu shortcut
class install(_install):
    def run(self):
        _install.run(self)
        if self.dry_run:
            return
        if sys.platform.startswith('linux'):
            icon_path = os.path.join(
                self.install_purelib, 'photini/data/icon_48.png')
            temp_file = os.path.join(
                self.install_purelib, 'photini/photini.desktop')
            with open(temp_file, 'w') as of:
                for line in open('src/linux/photini.desktop').readlines():
                    of.write(line)
                of.write('Icon=%s' % icon_path)
            self.spawn(['desktop-file-install', '--delete-original', temp_file])

cmdclass['install'] = install

# add command to extract strings for translation
class extract_messages(Command):
    description = 'extract localizable strings from the project code'
    user_options = [
        ('output-file=', 'o',
         'name of the output file'),
        ('input-dir=', 'i',
         'directory that should be scanned for Python files'),
    ]

    def initialize_options(self):
        self.output_file = None
        self.input_dir = None

    def finalize_options(self):
        if not self.output_file:
            raise DistutilsOptionError('no output file specified')
        if not self.input_dir:
            raise DistutilsOptionError('no input directory specified')

    def run(self):
        inputs = []
        for name in os.listdir(self.input_dir):
            base, ext = os.path.splitext(name)
            if ext == '.py':
                inputs.append(os.path.join(self.input_dir, name))
        out_dir = os.path.dirname(self.output_file)
        self.mkpath(out_dir)
        temp_file = os.path.join(out_dir, 'temp_latin9.ts')
        subprocess.check_call(
            ['pylupdate4', '-verbose'] + inputs + ['-ts', temp_file])
        subprocess.check_call(['iconv', '-f', 'ISO-8859-15', '-t', 'UTF-8',
                               '-o', self.output_file, temp_file])

cmdclass['extract_messages'] = extract_messages
command_options['extract_messages'] = {
    'output_file' : ('setup.py', 'build/messages/photini.ts'),
    'input_dir'   : ('setup.py', 'src/photini'),
    }

with open('README.rst') as ldf:
    long_description = ldf.read()
url = 'https://github.com/jim-easterbrook/Photini'

setup(name = 'Photini',
      version = next_release,
      author = 'Jim Easterbrook',
      author_email = 'jim@jim-easterbrook.me.uk',
      url = url,
      download_url = url + '/archive/Photini-' + next_release + '.tar.gz',
      description = 'Simple photo metadata editor',
      long_description = long_description,
      classifiers = [
          'Development Status :: 4 - Beta',
          'Intended Audience :: End Users/Desktop',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Topic :: Multimedia :: Graphics',
          ],
      license = 'GNU GPL',
      platforms = ['POSIX', 'MacOS', 'Windows'],
      packages = ['photini'],
      package_dir = {'' : 'src'},
      package_data = {
          'photini' : [
              'data/*.html', 'data/*.txt', 'data/*.js',   'data/*.png'],
          },
      cmdclass = cmdclass,
      command_options = command_options,
      entry_points = {
          'gui_scripts' : [
              'photini = photini.editor:main',
              ],
          },
      install_requires = ['appdirs >= 1.3', 'six >= 1.8'],
      extras_require = {
          'flickr'  : ['flickrapi >= 2.0'],
          'importer': ['gphoto2 >= 0.10'],
          'picasa'  : ['requests >= 2.5', 'requests-oauthlib >= 0.4']
          },
      )
