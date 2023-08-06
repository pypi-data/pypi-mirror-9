#!/usr/bin/env python3

# Copyright Louis Paternault 2011-2014
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>. 1

"""Set up working environments to edit a file

Example of configuration file, to edit .tex files. This supposes that template
~/.devoir/templates/pdf exists.

> $ cat ~/.devoir/ftplugins/tex.cfg
>     [config]
>
>     cwd = {dirname}
>
>     [process]
>
>     pre = test -e {basename}.pdf || cp {configdir}/templates/pdf {basename}.pdf
>     cmd1 = evince {basename}.pdf &
>     cmd2 = screen $EDITOR {basename}.tex
>     cmd3 = screen latexmk -pvc {basename}

"""

import argparse
import configparser
import glob
import logging
import os
import shutil
import subprocess
import sys

import devoir

LOGGER = logging.getLogger(devoir.__name__)
LOGGER.addHandler(logging.StreamHandler())

DEVOIRRC = os.path.expanduser('~/.devoir')

class DevoirException(Exception):
    """Generic exception for this program."""
    pass

class NoPlugin(DevoirException):
    """No plugin found."""

    def __init__(self, extension, filenames):
        super().__init__()
        self.extension = extension
        self.filenames = filenames

    def __str__(self):
        return "No plugin found for extension '{}' (I tried {}).".format(
            self.extension,
            ",".join([
                "'{}'".format(filename)
                for filename
                in self.filenames
                ]),
            )

def load_plugin(extension):
    """Load plugin for extension.

    The plugin (as a dict of its options), filled with default values if
    necessary."""
    config = configparser.ConfigParser()
    config.read_dict({
        'process': {},
        'config': {
            'cwd': '.',
            },
        })
    filename = os.path.join(
        DEVOIRRC,
        'ftplugins',
        '{}.cfg'.format(extension)
        )
    if not os.path.exists(filename):
        raise NoPlugin(extension, [filename])
    config.read([filename])
    return config

def commandline_parser():
    """Return an argument parser"""

    parser = argparse.ArgumentParser(
        description="Prepare working environment to edit a file."
        )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s ' + devoir.VERSION,
        )

    parser.add_argument(
        'template',
        nargs="?",
        help=(
            "Template to use: if set, this file is copied as FILE before "
            "editing it"
            ),
        default=None
        )

    parser.add_argument(
        'file',
        nargs=1,
        help="File to edit."
        )

    return parser

def get_extension(filename):
    """Return (dirname, basename, extension).

    The extension is the actual or guessed extension of the argument.

    - If filename has an extension (i.e. ends with dot-something), return it.
    - Otherwise, if only one plugin matches filename (i.e. if there exist only
      one plugin 'foo' such that file 'filename.foo' exists, return this
      extension.
    - Otherwise, raise an exception.
    """
    if '.' in os.path.basename(filename):
        splitted = os.path.basename(filename).split('.')
        return (
            os.path.dirname(filename),
            '.'.join(splitted[0:-1]),
            splitted[-1],
            )

    possible = []
    for plugin_name in glob.glob(os.path.join(DEVOIRRC, 'ftplugins', '*.cfg')):
        extension = os.path.basename(plugin_name)[0:-len('.cfg')]
        if os.path.exists('{}.{}'.format(filename, extension)):
            possible.append(extension)
    if len(possible) == 1:
        return (
            os.path.dirname(filename),
            os.path.basename(filename),
            possible[0],
            )

    raise Exception('No file named "{}".'.format(filename))

def main():
    """Main function"""

    try:
        options = commandline_parser().parse_args(sys.argv[1:])
        template, filename = options.template, options.file[0]

        (dirname, basename, extension) = get_extension(filename)
        filename = '{}.{}'.format(os.path.join(dirname, basename), extension)
        plugin = load_plugin(extension)

        # Copy template
        if not os.path.exists(filename):
            if not template:
                template = os.path.join(
                    DEVOIRRC,
                    'templates',
                    format(extension)
                    )
            if os.path.exists(template):
                shutil.copyfile(template, filename)
            else:
                # Just touch the file
                with open(filename, 'w') as __file:
                    pass

        # Building format dictionary
        format_dict = {
            'basename': basename,
            'dirname': os.path.abspath(dirname),
            'filename' : filename,
            'configdir': DEVOIRRC,
            }

        # Process
        for command in plugin['process'].items():
            command = command[1].format(**format_dict) # pylint: disable=star-args
            sys.stderr.write('{}\n'.format(command))
            subprocess.call(
                os.path.expandvars(command),
                shell=True,
                cwd=plugin['config']['cwd'].format(**format_dict), # pylint: disable=star-args
                )

    except DevoirException as error:
        LOGGER.error(str(error))
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
