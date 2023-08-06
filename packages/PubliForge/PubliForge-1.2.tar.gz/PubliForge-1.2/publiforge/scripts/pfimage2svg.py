#!/usr/bin/env python
# $Id: pfimage2svg.py 6479e6226e36 2014/12/12 09:35:16 Patrick $
"""Console script to embed an image into a SVG."""

import logging
from argparse import ArgumentParser
from os import makedirs
from os.path import exists, expanduser, isfile, splitext, dirname, basename
from shutil import copyfile
from locale import getdefaultlocale
import struct

from ..lib.utils import _, localizer, execute


__credits__ = '(c) Prismallia http://www.prismallia.fr, 2014'


LOG = logging.getLogger(__name__)


# =============================================================================
def main():
    """Main function."""
    # Parse arguments
    parser = ArgumentParser(description='Embed an image into a SVG.')
    parser.add_argument('img_file', help='image file to embed')
    parser.add_argument('svg_file', help='SVG file')
    parser.add_argument('--lang', dest='lang', help='user language')
    parser.add_argument(
        '--bitmap', dest='ext', help='extension of the embedded image',
        default='png', choices=('png', 'jpg'))
    parser.add_argument(
        '--size', dest='size', help='size for the embedded image')
    parser.add_argument(
        '--optimize', dest='opt',
        choices=('0', '1', '2', '3', '4', '5', '6', '7'), default='0',
        help='optimization level (default=0)')
    parser.add_argument(
        '--log-level', dest='log_level', help='log level', default='INFO',
        choices=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'))
    parser.add_argument('--log-file', dest='log_file', help='log file')
    args = parser.parse_args()
    if not isfile(args.img_file):
        parser.print_usage()
        exit(2)

    # Initialize log
    my_format = '%(message)s (%(levelname)s)'
    if args.log_file:
        logging.basicConfig(
            filename=expanduser(args.log_file), filemode='w',
            level=args.log_level, format=my_format)
    else:
        logging.basicConfig(level=args.log_level, format=my_format)

    # Embed
    exit(Image2Svg(args).embed(args.img_file, args.svg_file))


# =============================================================================
class Image2Svg(object):
    """Class to embed an image into a SVG on command-line."""

    # -------------------------------------------------------------------------
    def __init__(self, args):
        """Constructor method."""
        self._args = args

    # -------------------------------------------------------------------------
    def embed(self, img_file, svg_file):
        """Start process.

        :param img_file: (string)
            Path to image to embed.
        :param svg_file: (string)
            Path to SVG file to create.
        :return: (integer)
            Error code.
        """
        if not exists(dirname(svg_file)):
            makedirs(dirname(svg_file))

        # SVG 2 SVG
        img_ext = splitext(img_file)[1]
        if img_ext == '.svg':
            return self._copy_svg(img_file, svg_file)

        # Bitmap to SVG
        bitmap_file = '%s.svg.%s' % (splitext(svg_file)[0], self._args.ext)
        self._convert_bitmap(img_file, bitmap_file)
        return self._create_svg(bitmap_file, svg_file)

    # -------------------------------------------------------------------------
    def _copy_svg(self, img_file, svg_file):
        """Copy a SVG file, eventually with its embedded bitmap file.

        :param img_file: (string)
            Path to image to embed.
        :param svg_file: (string)
            Path to SVG file to create.
        :return: (integer)
            Error code.
        """
        copyfile(img_file, svg_file)

        root = splitext(img_file)[0]
        for ext in ('.svg.png', '.svg.jpg', '.png', '.jpg'):
            bitmap_file = '%s%s' % (root, ext)
            if not exists(bitmap_file):
                continue
            # Create bitmap file
            if ext.endswith(self._args.ext) and not self._args.size:
                new_bitmap_file = '%s%s' % (splitext(svg_file)[0], ext)
                copyfile(bitmap_file, new_bitmap_file)
            else:
                new_bitmap_file = \
                    '%s.svg.%s' % (splitext(svg_file)[0], self._args.ext)
                error = self._convert_bitmap(bitmap_file, new_bitmap_file)
                if error:
                    return error

            # Change the link in SVG file
            with open(svg_file, 'r') as hdl:
                content = hdl.read()
            content = content.replace(
                basename(bitmap_file), basename(new_bitmap_file))
            with open(svg_file, 'w') as hdl:
                hdl.write(content)
            return 0

    # -------------------------------------------------------------------------
    def _convert_bitmap(self, old_bitmap, new_bitmap):
        """Convert the bitmap file.

        :param old_bitmap: (string)
            Path to the source bitmap.
        :param new_bitmap: (string)
            Path to the destination bitmap.
        :return: (integer)
            Error code.
        """
        # Convert
        cmd = ['nice', 'convert', old_bitmap]
        if self._args.size:
            cmd += ['-geometry', self._args.size]
        cmd += [new_bitmap]
        error = execute(cmd)
        if error[1]:
            LOG.error(self._translate(error[0] or error[1]))
            return 2

        # Optimize
        if self._args.opt == '0':
            return 0
        ext = splitext(new_bitmap)[1]
        if ext == '.jpg':
            execute(['nice', 'jpegoptim', '-q', new_bitmap])
        elif ext == '.png':
            execute(['nice', 'optipng', '-o', self._args.opt, new_bitmap])
            execute(['nice', 'advpng', '-z', '-q', '-4', new_bitmap])
        return 0

    # -------------------------------------------------------------------------
    def _create_svg(self, bitmap_file, svg_file):
        """Create a SVG file which embeds the ``bitmap_file`` file.

        :param bitmap_file: (string)
            Path to image to embed.
        :param svg_file: (string)
            Path to SVG file to create.
        :return: (integer)
            Error code.
        """
        # Get bitmap size
        width, height = self._image_size(bitmap_file)
        if not width:
            LOG.error(self._translate(_('Cannot find the image size!')))
            return 2

        # Create SVG file
        content = \
            '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'\
            '<svg\n'\
            '  xmlns:svg="http://www.w3.org/2000/svg"\n'\
            '  xmlns:xlink="http://www.w3.org/1999/xlink"\n'\
            '  xmlns="http://www.w3.org/2000/svg"\n'\
            '  version="1.1" id="svg1"\n'\
            '  width="{w}" height="{h}"\n'\
            '  viewBox="0 0 {w} {h}">\n'\
            '    <image id="image1" xlink:href="{f}" x="0" y="0"'\
            ' width="{w}" height="{h}"/>\n'\
            '</svg>'.format(w=width, h=height, f=basename(bitmap_file))

        with open(svg_file, "w") as hdl:
            hdl.write(content)

        return 0

    # -------------------------------------------------------------------------
    @classmethod
    def _image_size(cls, img_file):
        """Return the size of image ``img_file``.

        :param img_file: (string)
            Full path to image to process.
        :return: (tuple or ``None``)
            A tuple such as ``(width, height)``.
        """
        ext = splitext(img_file)[1]
        if ext not in ('.jpg', '.png', '.gif'):
            return 0, 0
        with open(img_file, 'rb') as hdl:
            head = hdl.read(24)
            if ext == '.png':
                check = struct.unpack('>i', head[4:8])[0]
                if check == 0x0d0a1a0a:
                    width, height = struct.unpack('>ii', head[16:24])
                    return int(round(width)), int(round(height))
            if ext == '.gif':
                width, height = struct.unpack('<HH', head[6:10])
                return int(round(width)), int(round(height))
            else:
                try:
                    hdl.seek(0)
                    size = 2
                    ftype = 0
                    while not 0xc0 <= ftype <= 0xcf:
                        hdl.seek(size, 1)
                        byte = hdl.read(1)
                        while ord(byte) == 0xff:
                            byte = hdl.read(1)
                        ftype = ord(byte)
                        size = struct.unpack('>H', hdl.read(2))[0] - 2
                    # We are at a SOFn block
                    hdl.seek(1, 1)  # Skip `precision' byte.
                    height, width = struct.unpack('>HH', hdl.read(4))
                    return int(round(width)), int(round(height))
                except Exception:  # pylint: disable = locally-disabled, W0703
                    return 0, 0
        return 0, 0

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
