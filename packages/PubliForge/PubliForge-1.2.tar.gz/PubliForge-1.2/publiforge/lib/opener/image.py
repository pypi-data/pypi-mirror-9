# $Id: image.py 9fda6039f483 2014/11/12 09:37:40 Patrick $
"""Web image opener."""

from webhelpers2.html import literal

from . import Opener as OpenerBase


# =============================================================================
class Opener(OpenerBase):
    """Class to operate on Web images."""
    # pylint: disable = locally-disabled, too-many-public-methods

    # -------------------------------------------------------------------------
    def match(self, fullname, content=None):
        """Check whether this opener matches with the file ``fullname``.

        See parent method :meth:`Opener.match`.
        """
        return \
            fullname[-4:] in ('.png', '.gif', '.jpg', '.jpeg', '.svg'), content

    # -------------------------------------------------------------------------
    def read(self, request, storage, path, content=None):
        """Literal XHTML to display the file content.

        See parent method :meth:`~.lib.opener.Opener.read`.
        """
        return literal(
            '<div><img src="%s" alt="%s"/></div>' %
            (request.route_path(
                'file_download', storage_id=storage['storage_id'], path=path),
             path))

    # -------------------------------------------------------------------------
    @classmethod
    def can_write(cls):
        """Return ``True`` if it can simply modify the file.

        See parent method :meth:`~.lib.opener.Opener.can_write`.
        """
        return False

    # -------------------------------------------------------------------------
    @classmethod
    def css(cls, mode, request=None):
        """Return a list of CSS files for the mode ``mode``.

        See parent method :meth:`~.lib.opener.Opener.css`.
        """
        # pylint: disable = locally-disabled, unused-argument
        return tuple()

    # -------------------------------------------------------------------------
    @classmethod
    def javascript(cls, mode, request=None):
        """Return list of JavaScript files for the mode ``mode``.

        See parent method :meth:`~.lib.opener.Opener.javascript`.
        """
        # pylint: disable = locally-disabled, unused-argument
        return tuple()
