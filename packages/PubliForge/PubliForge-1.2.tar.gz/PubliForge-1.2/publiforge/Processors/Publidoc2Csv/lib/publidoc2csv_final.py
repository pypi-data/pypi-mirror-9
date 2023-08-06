# $Id: publidoc2csv_final.py 3c92085d69aa 2015/02/17 18:07:19 Patrick $
"""LePrisme finalization script."""

from os.path import basename

from publiforge.lib.utils import _


# =============================================================================
def main(processor):
    """Finalization.

    :param processor: (Processor object)
        Processor object.
    """
    processor.build.log(
        _('dummy finalization of "${f}"', {'f': basename(processor.output)}))
