#!/usr/bin/env python
# $Id: pftexmath.py 7981fd623a54 2015/02/21 08:15:22 Patrick $
"""Console script to convert LaTeX formulas."""

import logging
from argparse import ArgumentParser
from os import makedirs
from os.path import expanduser, isdir, exists, join, dirname, basename
from os.path import splitext
from glob import iglob
from locale import getdefaultlocale
import re

from ..lib.utils import _, localizer, execute


__credits__ = '(c) Prismallia http://www.prismallia.fr, 2014'


LOG = logging.getLogger(__name__)


# =============================================================================
def main():
    """Main function."""
    # Parse arguments
    parser = ArgumentParser(description='Convert LaTeX formulas.')
    parser.add_argument('fid', help='file ID of processed file')
    parser.add_argument('tex_dir', help='directory containing LaTeX files')
    parser.add_argument(
        '--mode', dest='mode', help='conversion mode', default='png',
        choices=('png',))
    parser.add_argument(
        '--factor', dest='factor', help='magnification factor',
        type=float, default=.3)
    parser.add_argument('--output', dest='output', help='output directory')
    parser.add_argument(
        '--done-tag', dest='done_tag', help='tag to mark used files')
    parser.add_argument('--lang', dest='lang', help='user language')
    parser.add_argument(
        '--log-level', dest='log_level', help='log level', default='INFO',
        choices=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'))
    parser.add_argument('--log-file', dest='log_file', help='log file')
    args = parser.parse_args()
    if not isdir(args.tex_dir):
        parser.print_usage()
        exit(2)

    # Initialize log
    log_format = '%(message)s (%(levelname)s)'
    if args.log_file:
        logging.basicConfig(
            filename=expanduser(args.log_file), filemode='w',
            level=args.log_level, format=log_format)
    else:
        logging.basicConfig(level=args.log_level, format=log_format)

    # Process
    exit(TexMath(args).start(args.tex_dir))


# =============================================================================
class TexMath(object):
    """Class to convert LaTeX formulas on command-line."""

    # -------------------------------------------------------------------------
    def __init__(self, args):
        """Constructor method."""
        self.fid = args.fid
        self._args = args
        self._maths = None

    # -------------------------------------------------------------------------
    def start(self, tex_dir):
        """Start conversion.

        :param text_dir: (string)
            Path to directory containing LaTeX files.
        :return: (integer)
            Error code.
        """
        # Check arguments
        if self._args.mode == 'png' and not self._args.output:
            LOG.critical(self._translate(_(
                '${f}: you must define an output directory for ${m} mode',
                {'f': self.fid, 'm': self._args.mode})))
            return 2
        if self._args.output and not exists(self._args.output):
            makedirs(self._args.output)

        # Create images
        LOG.info(self._translate(
            _('${f}: LaTeX formulas conversion', {'f': self.fid})))
        self._maths = {}
        for filename in iglob(join(tex_dir, '%s-tex*.tex' % self.fid)):
            if not self._tex2png(filename):
                return 2

        # Update HTML files
        if self._maths:
            LOG.info(self._translate(
                _('${f}: updating image sizes', {'f': self.fid})))
            for filename in iglob(join(tex_dir, '%s*.*html' % self.fid)):
                with open(filename, 'r') as hdl:
                    content = hdl.read()
                for math_id in self._maths:
                    content = content.replace(
                        'title="${%s}"' % math_id,
                        'style="height: %dpx; vertical-align: %dpx"'
                        % self._maths[math_id])
                with open(filename, 'w') as hdl:
                    hdl.write(content)

        return 0

    # -------------------------------------------------------------------------
    def _tex2png(self, tex_file):
        """Convert a LaTeX file into a PNG file.

        :param tex_file: (string)
            LaTeX file to process.
        :return: (boolean)
        """
        # Look for image ID
        math_id = None
        for line in open(tex_file, 'r'):
            if line.startswith('% math_id = '):
                math_id = line.replace('% math_id = ', '').strip()
                break
        if not math_id:
            LOG.error(self._translate(_(
                'Unknown image ID for LaTeX file "${f}"',
                {'f': basename(tex_file)})))
            return False

        # Convert into a DVI file
        result = execute(
            ['nice', 'latex', '-interaction=nonstopmode', '-halt-on-error',
             basename(tex_file)], cwd=dirname(tex_file))
        if result[1]:
            LOG.error(self._translate(result[0] or result[1]))
            return False

        # Convert into a Png file
        result = execute([
            'nice', 'dvipng', '--depth', '--height', '-bg', 'Transparent',
            '-D', '200',
            '-o', join(self._args.output, '%s.png' % math_id),
            '%s.dvi' % splitext(tex_file)[0]])
        if result[1]:
            LOG.error(self._translate(result[0] or result[1]))
            return False

        # Save height and depth
        match = re.search(r'depth=(-?\d+) height=(\d+)', result[0])
        if match is None:
            LOG.error(self._translate(_(
                'size is missing for formula "${i}"', {'i': math_id})))
            return False
        self._maths[math_id] = (
            round((int(match.group(1)) + int(match.group(2))) *
                  self._args.factor),
            -round(int(match.group(1)) * self._args.factor))

        return True

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
