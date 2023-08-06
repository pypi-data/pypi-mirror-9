# $Id: publidoc2csv_init.py 3c92085d69aa 2015/02/17 18:07:19 Patrick $
"""LePrisme initialization script."""

from os.path import basename

from publiforge.lib.utils import _


# =============================================================================
def main(processor):
    """Initialization.

    :param processor: (Processor object)
        Processor object.
    """
    processor.build.log(
        _('dummy initialization of "${f}"', {'f': basename(processor.output)}))
