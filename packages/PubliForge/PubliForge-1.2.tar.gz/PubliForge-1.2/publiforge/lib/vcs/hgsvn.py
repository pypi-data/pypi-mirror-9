# $Id: hgsvn.py 423387b2062e 2014/07/27 21:39:58 Patrick $
"""Storage with Subversion (via Mercurila) Version Control management."""

import logging
from urlparse import urlparse, urlunparse
from mercurial import hg, extensions
from subvertpy import SubversionException

from .hg import VcsMercurial, VcsMercurialUi


LOG = logging.getLogger(__name__)


# =============================================================================
class VcsHgSubversion(VcsMercurial):
    """Version control system with Subversion via HgSubversion."""

    engine = 'hgsvn'

    # -------------------------------------------------------------------------
    def __init__(self, path, url, user_id=None, password=None):
        """Constructor method."""
        # pylint: disable = locally-disabled, unpacking-non-sequence
        scheme, netloc, urlpath, params, query, fragment = urlparse(str(url))
        url = urlunparse((
            'svn+%s' % scheme, netloc, urlpath, params, query, fragment))
        super(VcsHgSubversion, self).__init__(path, url, user_id, password)
        try:
            extensions.load(self._ui, 'hgsubversion', '')
        except ImportError as error:
            LOG.error(error)
            return
        self._ui.setconfig('extensions', 'hgsubversion', '')
        self._ui.setconfig('hgsubversion', 'stupid', 'yes')

    # -------------------------------------------------------------------------
    def clone(self, handler=None):
        """Create a copy of an existing repository in a directory.

        See abstract function :meth:`~.lib.vcs.Vcs.clone`.
        """
        try:
            return super(VcsHgSubversion, self).clone(handler)
        except SubversionException as error:
            if handler is not None:
                handler.report('error', error)
            return error

    # -------------------------------------------------------------------------
    def last_change(self):
        """Return the last change on the repository.

        See :meth:`~.hg.VcsMercurial.last_change`.
        """
        change = super(VcsHgSubversion, self).last_change()
        return change[0], change[1], change[2].partition('@')[0]

    # -------------------------------------------------------------------------
    def log(self, path, filename, limit=1):
        """Show revision history of file ``filename``.

        See :meth:`~.hg.VcsMercurial.log`.
        """
        my_log = super(VcsHgSubversion, self).log(path, filename, limit)
        return my_log and \
            [(k[0], k[1], k[2].partition('@')[0], k[3]) for k in my_log]

    # -------------------------------------------------------------------------
    def directory_log(self, path, quick=False):
        """List all files of a directory with VCS informations.

        See :meth:`~.lib.vcs.Vcs.directory_log`.
        """
        dirs, files = super(VcsHgSubversion, self).directory_log(path, quick)
        return [[k[0], k[1], k[2], k[3], k[4], k[5].partition('@')[0], k[6]]
                for k in dirs], \
            [[k[0], k[1], k[2], k[3], k[4], k[5].partition('@')[0], k[6]]
             for k in files]

    # -------------------------------------------------------------------------
    def _named_ui_repo(self, name, handler=None):
        """Get an UI and a repository for a specific name.

        :param name: (string)
            Name for VCS access.
        :param handler: (:class:`~.lib.handler.Handler` instance, optional)
            Owner of this action.
        :return: (:class:`VcsMercurialUi`, :class:`mercurial.repo`)
        """
        myui = VcsMercurialUi()
        myui.handler = handler
        myui.setconfig('extensions', 'hgsubversion', '')
        myui.setconfig('hgsubversion', 'stupid', 'yes')
        myui.setconfig('ui', 'interactive', 'no')
        myui.setconfig('ui', 'username', name.encode('utf8'))
        myui.setconfig('web', 'cacerts', '')
        repo = hg.repository(myui, self.path)
        return myui, repo
