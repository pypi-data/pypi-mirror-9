# $Id: publidoc2csv2_post.py 3c92085d69aa 2015/02/17 18:07:19 Patrick $
"""LePrisme postprocess script."""

from publiforge.lib.utils import _


# =============================================================================
def main(processor, filename, fid, data):
    """Post process script.

    :param processor: (:class:`Processor` instance)
        Processor object.
    :param filename: (string)
        Relative path to the original file to transform.
    :param fid: (string)
        File identifier.
    :param data: (string or :class:`lxml.etree.ElementTree` object)
        Data to transform in a string or in a tree.
    :return: (string, :class:`lxml.etree.ElementTree` object or ``None``)
        Modified data or ``None`` if fails.
    """
    # pylint: disable = locally-disabled, W0613
    processor.build.log(_('${f}: dummy postprocess 2 of "${f}"', {'f': fid}))
    return data
