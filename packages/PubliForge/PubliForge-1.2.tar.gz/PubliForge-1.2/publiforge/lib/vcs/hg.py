# $Id: hg.py a0e4a521a9df 2015/01/05 16:12:50 Patrick $
"""Storage with Mercurial Version Control management."""

import logging
from os import remove, renames
from os.path import exists, join, isdir, getmtime, normpath
from shutil import rmtree
from datetime import datetime
from urllib2 import HTTPError, URLError
from mercurial import ui, hg, commands
from mercurial.error import Abort, RepoError, ParseError
from tempfile import mkdtemp

from pyramid.i18n import TranslationString

from ...lib.utils import _
from ...lib.vcs import Vcs


LOG = logging.getLogger(__name__)


# =============================================================================
class VcsMercurialUi(ui.ui):
    """Override Mercurial ui class for PubliForge use."""
    # pylint: disable = locally-disabled, R0904

    # -------------------------------------------------------------------------
    def __init__(self, src=None):
        """Contructor method."""
        super(VcsMercurialUi, self).__init__(src)
        self.handler = None

    # -------------------------------------------------------------------------
    def write(self, *args, **opts):
        """Write args in log as informations."""
        for arg in args:
            arg = arg.strip()
            if arg:
                LOG.info(arg)

    # -------------------------------------------------------------------------
    def write_err(self, *args, **opts):
        """Write args in log as errors."""
        for arg in args:
            arg = arg.strip()
            if arg:
                LOG.error(arg)
                if self.handler is not None:
                    self.handler.report('error', arg)


# =============================================================================
class VcsMercurialUiLog(VcsMercurialUi):
    """Ui class to retrieve file information."""
    # pylint: disable = locally-disabled, too-many-public-methods

    # -------------------------------------------------------------------------
    def __init__(self, src=None):
        """Constructor method."""
        super(VcsMercurialUiLog, self).__init__(src)
        self.infos = []
        self.log = []
        self._entry = None
        self._description = False

    # -------------------------------------------------------------------------
    def write(self, *args, **opts):
        """This method collects log information."""
        for arg in args:
            if arg.startswith('changeset:'):
                if self._entry is not None:
                    self._update_infos()
                self._entry = ['', int(arg[10:].partition(':')[0]), '', '']
            elif arg.startswith('user:'):
                self._entry[2] = arg[5:].strip()
            elif arg.startswith('date:'):
                self._entry[0] = arg[5:-6].strip()
            elif arg.startswith('files:'):
                try:
                    self._entry[3] = ' %s ' % arg[6:].strip().decode('utf8')
                except UnicodeDecodeError:
                    self._entry[3] = ' - '
            elif arg.startswith('summary:'):
                self._entry[3] = arg[8:].strip()
                self.log.append(self._entry)
                self._entry = None
            elif arg.startswith('description:'):
                self._description = True
            elif self._description:
                self._update_infos(arg)
                self._entry = None

    # -------------------------------------------------------------------------
    def _update_infos(self, arg=''):
        """Update ``self.infos`` list."""
        for name in self.infos:
            if name in self._entry[3] \
               and self.infos[name][1] < self._entry[1]:
                self.infos[name] = (
                    self._entry[0], self._entry[1],
                    self._entry[2], arg.strip())
        self._description = False
        self.log.append(self._entry)


# =============================================================================
class VcsMercurial(Vcs):
    """Version control system with Mercurial."""

    engine = 'hg'

    # -------------------------------------------------------------------------
    def __init__(self, path, url, user_id=None, password=None):
        """Constructor method."""
        super(VcsMercurial, self).__init__(path, url, user_id, password)
        self._ui = VcsMercurialUi()
        self._ui.setconfig('ui', 'interactive', 'no')
        self._ui.setconfig('ui', 'username', '-')
        self._ui.setconfig('web', 'cacerts', '')

    # -------------------------------------------------------------------------
    def clone(self, handler=None):
        """Create a copy of an existing repository in a directory.

        See abstract function :meth:`~.lib.vcs.Vcs.clone`.
        """
        self._ui.handler = handler
        try:
            commands.clone(self._ui, self._full_url(), self.path)
        except (Abort, RepoError, HTTPError, URLError,
                AssertionError, OSError) as error:
            if handler is not None:
                handler.report('error', error)
            return error
        remove(join(self.path, '.hg', 'hgrc'))

    # -------------------------------------------------------------------------
    def pull_update(self, handler):
        """Pull changes and update.

        See abstract function :meth:`~.lib.vcs.Vcs.pull_update`.
        """
        if not exists(self.path):
            return
        try:
            if self.engine == 'local':
                commands.update(self._ui, self._repo(handler))
            else:
                commands.pull(
                    self._ui, self._repo(handler), self._full_url(),
                    update=True)
        except (Abort, RepoError, HTTPError, URLError,
                OSError, AttributeError) as error:
            return handler.report('error', error)

    # -------------------------------------------------------------------------
    def commit_push(self, message, user_id, password, name, handler):
        """Commit and push changes.

        See abstract method :meth:`~.lib.vcs.Vcs.commit_push`.
        """
        if not exists(self.path):
            return
        myui, repo = self._named_ui_repo(name or user_id, handler)
        message = message or '-'
        try:
            commands.commit(myui, repo, message=message.encode('utf8'))
            if self.engine != 'local':
                commands.push(myui, repo, self._full_url(user_id, password))
        except (Abort, RepoError, HTTPError, URLError, OSError) as error:
            return handler.report('error', error)

    # -------------------------------------------------------------------------
    def revert_all(self, handler):
        """Revert all files of the repository."""
        if not exists(self.path):
            return
        commands.revert(
            self._ui, self._repo(handler), all=True, no_backup=True)
        commands.update(self._ui, self._repo(handler), clean=True)

    # -------------------------------------------------------------------------
    def backout(self, name, handler):
        """Reverse effect of earlier changeset.

        See :meth:`~.lib.vcs.Vcs.backout`.
        """
        if not exists(self.path):
            return
        myui, repo = self._named_ui_repo(name, handler)
        try:
            commands.backout(
                myui, repo, rev='tip', message='Previous changeset canceled')
        except (Abort, RepoError, OSError) as error:
            return handler.report('error', error)

    # -------------------------------------------------------------------------
    def recover(self, handler):
        """Recover from an interrupted commit or pull."""
        commands.recover(self._ui, self._repo(handler))

    # -------------------------------------------------------------------------
    def last_change(self):
        """Return the last change on the repository.

        See :meth:`~.lib.vcs.Vcs.last_change`.
        """
        repo = self._repo()
        if repo is None:
            return (datetime.now(), -1, '-')
        ctx = repo['tip']
        if ctx.rev() == -1:
            return (datetime.fromtimestamp(getmtime(self.path)), -1, '-')
        return (datetime.fromtimestamp(ctx.date()[0]), ctx.rev(),
                ctx.user().partition('<')[0].decode('utf8'))

    # -------------------------------------------------------------------------
    def log(self, path, filename, limit=1):
        """Show revision history of file ``filename``.

        See :meth:`~.lib.vcs.Vcs.log`.
        """
        filename = self._log_path(path, filename)
        if filename is None:
            return

        # Collect information
        myui = VcsMercurialUiLog()
        myui.setconfig('ui', 'verbose', False)
        try:
            repo = hg.repository(myui, self.path)
        except RepoError:
            return
        try:
            commands.log(
                myui, repo, filename, limit=str(limit),
                follow=limit > 1 and not isdir(filename),
                date=None, rev=None, user=None)
        except (Abort, RepoError, HTTPError, URLError,
                OSError, TypeError) as error:
            return [(datetime.now(), '', '', str(error).decode('utf8'))]
        if not len(myui.log):
            return myui.log

        # Format information
        myui.log = sorted(myui.log, key=lambda k: k[1], reverse=True)[:limit]
        for k, entry in enumerate(myui.log):
            myui.log[k] = (
                datetime.strptime(entry[0], '%a %b %d %H:%M:%S %Y'),
                str(entry[1]), entry[2].partition('<')[0].decode('utf8'),
                entry[3].decode('utf8'))
        return myui.log

    # -------------------------------------------------------------------------
    def directory_log(self, path, quick=False):
        """List all files of a directory with VCS informations.

        See :meth:`~.lib.vcs.Vcs.directory_log`.
        """
        dirs, files = super(VcsMercurial, self).directory_log(path)
        if quick:
            return dirs, files

        # Collect information
        myui = VcsMercurialUiLog()
        myui.setconfig('ui', 'verbose', True)
        myui.infos = dict(
            [(' %s/' % normpath(join(path, k[0])), ('', -1, '', ''))
             for k in dirs] +
            [(' %s ' % normpath(join(path, k[0])), ('', -1, '', ''))
             for k in files])
        try:
            repo = hg.repository(myui, self.path)
        except RepoError:
            return dirs, files
        try:
            commands.log(myui, repo, self._log_path(path))
        except (Abort, RepoError, HTTPError, URLError, OSError, TypeError):
            return dirs, files

        # Format information
        for entry in dirs + files:
            name = ' %s%s' % (
                normpath(join(path, entry[0])),
                entry[1] == 'folder' and '/' or ' ')
            if name in myui.infos and myui.infos[name][1] > -1:
                try:
                    entry[3] = datetime.strptime(
                        myui.infos[name][0], '%a %b %d %H:%M:%S %Y')
                    entry[4] = myui.infos[name][1]
                    entry[5] = myui.infos[name][2].partition('<')[0]\
                        .decode('utf8')
                    entry[6] = myui.infos[name][3].decode('utf8')
                except ImportError:
                    pass
        return dirs, files

    # -------------------------------------------------------------------------
    def add(self, path, handler):
        """Add all new files in ``path``.

        See abstract function :meth:`~.lib.vcs.Vcs.add`.
        """
        path = self.full_path(path)
        if isinstance(path, TranslationString):
            return handler.report('error', path)
        if not exists(path):
            return
        warn = commands.add(self._ui, self._repo(handler), path)
        if warn:
            return handler.report('error', _('Rejected'))

    # -------------------------------------------------------------------------
    def rename(self, path, filename, new_name, handler):
        """Rename a file."""
        filename = self.full_path(path, filename)
        if isinstance(filename, TranslationString):
            return handler.report('error', filename)
        new_name = self.full_path(path, new_name)
        if isinstance(new_name, TranslationString):
            return handler.report('error', new_name)
        if exists(new_name):
            return handler.report('error', _('File already exists!'))
        try:
            commands.rename(self._ui, self._repo(handler), filename, new_name)
        except (HTTPError, URLError, OSError, ValueError) as error:
            return handler.report('error', error)
        except (Abort, RepoError, IOError):
            if exists(filename) and not exists(new_name):
                renames(filename, new_name)

    # -------------------------------------------------------------------------
    def remove(self, path, filename, handler):
        """Remove a file.

        See abstract function :meth:`~.lib.vcs.Vcs.remove`.
        """
        filename = self.full_path(path, filename)
        if isinstance(filename, TranslationString):
            return handler.report('error', filename)
        if not exists(filename):
            return
        try:
            commands.remove(
                self._ui, self._repo(handler), filename)
        except (Abort, RepoError, HTTPError, URLError, OSError) as error:
            return handler.report('error', error)
        if exists(filename):
            if isdir(filename):
                rmtree(filename)
            else:
                remove(filename)

    # -------------------------------------------------------------------------
    def revision(self, fullname, revision):
        """Retrieve a revision.

        See :meth:`~.lib.vcs.Vcs.revision`.
        """
        tmp_dir = mkdtemp(prefix='publiforge')
        tmp_fil = join(tmp_dir, 'output')
        err = commands.cat(
            self._ui, self._repo(), fullname, rev=revision, output=tmp_fil)
        if err:
            rmtree(tmp_dir)
            return
        with open(tmp_fil, 'rb') as hdl:
            content = hdl.read()
        rmtree(tmp_dir)
        return content

    # -------------------------------------------------------------------------
    def diff(self, fullname, revision):
        """Return differences between revision ``revision`` and current
        revision.

        See :meth:`~.lib.vcs.Vcs.diff`.
        """
        class Ui(VcsMercurialUi):
            """Ui class to retrieve file information."""
            # pylint: disable = locally-disabled, too-many-public-methods
            # pylint: disable = locally-disabled, bad-super-call
            def __init__(self, src=None):
                super(Ui, self).__init__(src)
                self.diff = ''

            def write(self, *args, **opts):
                self.diff += ''.join(args)

        myui = Ui()
        repo = hg.repository(myui, self.path)
        try:
            commands.diff(myui, repo, fullname, rev=[revision])
        except (RuntimeError, ParseError) as error:
            return str(error)

        try:
            return myui.diff.decode('utf8')
        except UnicodeDecodeError:
            return myui.diff.decode('latin1')
        return ''

    # -------------------------------------------------------------------------
    def _repo(self, handler=None):
        """Get a repository object.

        :param handler: (:class:`~.lib.handler.Handler` instance, optional)
            Owner of this action.
        :return: (:class:`mercurial.repo`)
        """
        if handler is not None:
            self._ui.handler = handler
        try:
            return hg.repository(self._ui, self.path)
        except RepoError as error:
            if handler is not None:
                handler.report('error', error)

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
        myui.setconfig('ui', 'interactive', 'no')
        myui.setconfig('ui', 'username', name.encode('utf8'))
        myui.setconfig('web', 'cacerts', '')
        repo = hg.repository(myui, self.path)
        return myui, repo


# =============================================================================
class VcsLocal(VcsMercurial):
    """Version control system for local files."""

    engine = 'local'

    # -------------------------------------------------------------------------
    def clone(self, handler=None):
        """Initialize a Mercurial repository and copy source.

        See abstract function :meth:`~.lib.vcs.Vcs.clone`.
        """
        self._ui.handler = handler
        try:
            commands.init(self._ui, self.path)
        except RepoError as error:
            if handler is not None:
                handler.report('error', error)
        repo = self._repo()
        commands.add(self._ui, repo)
        commands.commit(self._ui, repo, message='Initial commit')
