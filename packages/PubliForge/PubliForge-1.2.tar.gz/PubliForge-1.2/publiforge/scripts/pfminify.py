#!/usr/bin/env python
# $Id: pfminify.py 40834b953918 2015/02/11 16:42:18 Patrick $
"""Console script to minify CSS and Javascript files."""

import logging
from argparse import ArgumentParser
from os import remove
from os.path import expanduser, isfile, join, dirname, isabs, basename
from locale import getdefaultlocale

from ..lib.utils import _, localizer, execute


__credits__ = '(c) Prismallia http://www.prismallia.fr, 2014'


LOG = logging.getLogger(__name__)


# =============================================================================
def main():
    """Main function."""
    # Parse arguments
    parser = ArgumentParser(description='CSS and Javascript files.')
    parser.add_argument('file', nargs='+')
    parser.add_argument(
        '--log-level', dest='log_level', help='log level', default='INFO',
        choices=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'))
    parser.add_argument('--log-file', dest='log_file', help='log file')
    parser.add_argument('--lang', dest='lang', help='user language')
    args = parser.parse_args()
    if not args.file:
        parser.print_usage()
        exit(2)

    # Initialize log
    log_fmt = '%(message)s (%(levelname)s)'
    if args.log_file:
        logging.basicConfig(
            filename=expanduser(args.log_file), filemode='w',
            level=args.log_level, format=log_fmt)
    else:
        logging.basicConfig(level=args.log_level, format=log_fmt)

    # Process
    exit(Minify(args).start(args.file))


# =============================================================================
class Minify(object):
    """Class to minify CSS and Javascript files on command-line."""

    # -------------------------------------------------------------------------
    def __init__(self, args):
        """Constructor method."""
        self._args = args

    # -------------------------------------------------------------------------
    def start(self, files):
        """Start conversion.

        :param ini_files: (list)
            List of configuration files to process.
        :return: (integer)
            Error code.
        """
        for filename in files:
            if not isfile(filename):
                LOG.error(self._translate(
                    _('Unknown file "${n}".', {'n': basename(filename)})))
                return 2

            content = ''
            path = dirname(filename)
            with open(filename, 'r') as hdl:
                for name in hdl:
                    name = name.strip()
                    if not name:
                        continue
                    name = isabs(name) and name or join(path, name)
                    if not isfile(name):
                        LOG.error(self._translate(
                            _('Unknown file "${n}".', {'n': basename(name)})))
                        return 2
                    with open(name, 'r') as hdl2:
                        content += hdl2.read() + '\n\n'
                    remove(name)
            with open(filename, 'w') as hdl:
                hdl.write(content)
            result = execute(
                ['nice', 'yui-compressor', filename, '-o', filename])
            if result[1]:
                LOG.error(self._translate(result[0] or result[1]))
                return 2

        return 0

    # -------------------------------------------------------------------------
    def _translate(self, text):
        """Return ``text`` translated.

        :param text: (string)
            Text to translate.
        """
        return localizer(
            self._args.lang or getdefaultlocale()[0]).translate(text)


# =============================================================================
if __name__ == '__main__':
    main()
