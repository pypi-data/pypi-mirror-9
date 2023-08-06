# $Id: __init__.py 828a3c221ecf 2014/12/09 15:00:26 Patrick $
"""Version Control System library."""

import logging
from abc import ABCMeta, abstractmethod
from os import mkdir, makedirs, remove, renames, walk, listdir
from os.path import exists, join, normpath, getmtime, isfile, getsize, splitext
from locale import resetlocale
from datetime import datetime
from urlparse import urlparse, urlunparse
from shutil import rmtree, copy

from pyramid.i18n import TranslationString

from ...lib.utils import _, EXCLUDED_FILES, get_mime_type


LOG = logging.getLogger(__name__)


# =============================================================================
class Vcs(object):
    """Abstract base class for version control class."""

    __metaclass__ = ABCMeta
    engine = None

    # -------------------------------------------------------------------------
    def __init__(self, path, url, user_id=None, password=None):
        """Constructor method.

        :param path: (string)
             Path to local copy.
        :param url: (string)
            URL of source repository.
        :param user_id: (string, optional)
            User ID for clone/pull access.
        :param password: (string, optional)
            Password for clone/pull access.
        """
        resetlocale()
        self.path = str(normpath(path))
        self.url = str(url)
        self._user_id = str(user_id or '')
        self._password = str(password or '')

    # -------------------------------------------------------------------------
    def __repr__(self):
        """String representation."""
        return "<Vcs('%s', '%s', '%s', '%s')>" % (
            self.engine, self.path, self.url, self._user_id)

    # -------------------------------------------------------------------------
    @abstractmethod
    def clone(self, handler=None):
        """Create a copy of an existing repository in a directory. (abstract)

        :param handler: (:class:`~.lib.handler.Handler` instance, optional)
            Owner of this action.
        :return: (string)
            Error message or ``None`` if it succeeds.
        """
        pass

    # -------------------------------------------------------------------------
    @abstractmethod
    def pull_update(self, handler):
        """Pull changes and update. (abstract)

        :param handler: (:class:`~.lib.handler.Handler` instance)
            Owner of this action.
        :return: (string)
            Error message or ``None`` if it succeeds.
        """
        pass

    # -------------------------------------------------------------------------
    @abstractmethod
    def commit_push(self, message, user_id, password, name, handler):
        """Commit and push changes. (abstract)

        :param message: (string)
            Commit message.
        :param user_id: (string)
            User ID for VCS access.
        :param password: (string)
            Cleared password for VCS access.
        :param name: (string)
            Name for VCS access.
        :param handler: (:class:`~.lib.handler.Handler` instance)
            Owner of this action.
        :return: (string)
            Error message or ``None`` if it succeeds.
        """
        pass

    # -------------------------------------------------------------------------
    @abstractmethod
    def revert_all(self, handler):
        """Revert all files of the repository. (abstract)

        :param handler: (:class:`~.lib.handler.Handler` instance)
            Owner of this action.
        """
        pass

    # -------------------------------------------------------------------------
    @abstractmethod
    def backout(self, name, handler):
        """Reverse effect of earlier changeset. (abstract)

        :param name: (string)
            Name for VCS access.
        :param handler: (:class:`~.lib.handler.Handler` instance)
            Owner of this action.
        """
        pass

    # -------------------------------------------------------------------------
    @abstractmethod
    def recover(self, handler):
        """Recover from an interrupted commit or pull. (abstract)

        :param handler: (:class:`~.lib.handler.Handler` instance)
            Owner of this action.
        """
        pass

    # -------------------------------------------------------------------------
    @abstractmethod
    def last_change(self):
        """Return the last change on the repository. (abstract)

        :return: (tuple)
           A tuple such as ``(date, changeset, user)``.
        """
        pass

    # -------------------------------------------------------------------------
    @abstractmethod
    def log(self, path, filename, limit=1):
        """Show revision history of file ``filename``.

        :param path: (string)
            Relative path to file.
        :param filename: (string)
            Name of the file.
        :param limit: (integer, default=1)
            Maximum number of entries in log.
        :return: (list of tuples or string)
            Log or error message.

        Each tuple or entry is like ``(date, changeset, user, message)``.
        """
        pass

    # -------------------------------------------------------------------------
    def directory_log(self, path, quick=False):
        """List all files of a directory with VCS informations.

        :param path: (string)
            Relative path of the directory.
        :param quick: (boolean)
            ``True`` to have a quick information.
        :return: (tuple)
            A tuple such as ``(dirs, files)`` where ``dirs`` and ``files`` are
            lists such as ``[name, type, size, date, revision, user,
            message]``.
        """
        # pylint: disable = locally-disabled, unused-argument
        path = self.full_path(path).decode('utf8')

        def _update_information(names):
            """Update ``names`` list with date information."""
            infos = []
            for name in names:
                if name in EXCLUDED_FILES:
                    continue
                if not isinstance(name, unicode):
                    name = name.decode('utf8')
                fullname = join(path, name)
                try:
                    filetype = get_mime_type(fullname)[1]
                    size = len(listdir(fullname)) if filetype == 'folder' \
                        else getsize(fullname)
                    infos.append([
                        name, filetype, size,
                        datetime.fromtimestamp(getmtime(fullname)),
                        '-', '-', '-'])
                except OSError:
                    continue
            return infos

        try:
            dirs, files = walk(path).next()[1:]
        except UnicodeDecodeError, error:
            LOG.error(error)
            dirs, files = [], []
        return _update_information(dirs), _update_information(files)

    # -------------------------------------------------------------------------
    @abstractmethod
    def add(self, path, handler):
        """Add all new files in ``path``. (abstract)

        :param path: (string)
            Relative path to browse.
        :param handler: (:class:`~.lib.handler.Handler` instance)
            Owner of this action.
        :return: (string)
            Error message or ``None`` if it succeeds.
        """
        pass

    # -------------------------------------------------------------------------
    def create(self, seed, path, name, handler):
        """Create a new file according to the seed file.

        :param seed: (string)
            Full path to the seed file.
        :param path: (string)
            Relative path to directory to create.
        :param name: (string)
            Name of directory to create.
        :param handler: (:class:`~.lib.handler.Handler` instance)
            Owner of this action.
        """
        if splitext(name)[1] != splitext(seed)[1]:
            name += splitext(seed)[1]
        fullname = self.full_path(path, name)
        if isinstance(fullname, TranslationString):
            return handler.report('error', fullname)
        if exists(fullname):
            return handler.report(
                'error', _('File "${f}" already exists.', {'f': name}))
        copy(seed, fullname)
        self.add(path, handler)

    # -------------------------------------------------------------------------
    def duplicate(self, path, original, name, handler):
        """Duplicate the ``original`` file.

        :param path: (string)
            Relative path to directory to create.
        :param original: (string)
            Name of the original file.
        :param name: (string)
            Name of directory to create.
        :param handler: (:class:`~.lib.handler.Handler` instance)
            Owner of this action.
        """
        if splitext(name)[1] != splitext(original)[1]:
            name += splitext(original)[1]
        fulloriginal = self.full_path(path, original)
        if isinstance(fulloriginal, TranslationString):
            return handler.report('error', fulloriginal)
        if not exists(fulloriginal):
            return handler.report(
                'error', _('"${n}" does not exist.', {'n': original}))
        fullname = self.full_path(path, name)
        if exists(fullname):
            return handler.report(
                'error', _('File "${f}" already exists.', {'f': name}))
        print fulloriginal, fullname
        copy(fulloriginal, fullname)
        self.add(path, handler)

    # -------------------------------------------------------------------------
    def mkdir(self, path, name, handler):
        """Make the directroy ``name``.

        :param path: (string)
            Relative path to directory to create.
        :param name: (string)
            Name of directory to create.
        :param handler: (:class:`~.lib.handler.Handler` instance)
            Owner of this action.
        """
        name = self.full_path(path, name)
        if isinstance(name, TranslationString):
            return handler.report('error', name)
        if not exists(name):
            mkdir(name)

    # -------------------------------------------------------------------------
    @abstractmethod
    def rename(self, path, filename, new_name, handler):
        """Rename a file. (abstract)

        :param path: (string)
            Relative path to file to rename.
        :param filename: (string)
            Name of the file to remove.
        :param new_new: (string)
            New name.
        :param handler: (:class:`~.lib.handler.Handler` instance)
            Owner of this action.
        :return: (string)
            Error message or ``None`` if it succeeds.
        """
        pass

    # -------------------------------------------------------------------------
    @abstractmethod
    def remove(self, path, filename, handler):
        """Remove a file. (abstract)

        :param path: (string)
            Relative path to file to remove.
        :param filename: (string)
            Name of the file to remove.
        :param handler: (:class:`~.lib.handler.Handler` instance)
            Owner of this action.
        :return: (string)
            Error message or ``None`` if it succeeds.
        """
        pass

    # -------------------------------------------------------------------------
    @abstractmethod
    def revision(self, fullname, revision):
        """Retrieve a revision. (abstract)

        :param fullname: (string)
            Full name of the file.
        :param revision: (string)
            Revision number to retrieve.
        :return: (string)
            Content of the file.
        """
        pass

    # -------------------------------------------------------------------------
    @abstractmethod
    def diff(self, fullname, revision):
        """Return differences between revision ``revision`` and current
        revision. (abstract)

        :param fullname: (string)
            Full name of the file.
        :param revision: (string)
            Revision number to compare.
        :return: (string)
            Differences.
        """
        pass

    # -------------------------------------------------------------------------
    def full_path(self, *path):
        """Return normalized full path of ``path`` file or an error message if
        it is outside the storage.

        :param path: (strings)
            Path chunks.
        :return: (string or :class:`pyramid.i18n.TranslationString` instance)
            Full path or error message.
        """
        full_path = normpath(join(self.path, *path))
        if not full_path.startswith(self.path):
            return _('Out of storage!')
        return full_path.encode('utf8')

    # -------------------------------------------------------------------------
    def _full_url(self, user_id=None, password=None):
        """Return an URL with ``user_id`` and ``password``.

        :param user_id: (string)
            User ID for VCS access.
        :param password: (string)
            Password for VCS access.
        :return: (string)
            Full URL.
        """
        user_id = user_id or self._user_id
        if not user_id:
            return self.url
        # pylint: disable = locally-disabled, unpacking-non-sequence
        scheme, netloc, path, params, query, fragment = urlparse(str(self.url))
        netloc = '%s:%s@%s' % (user_id, password or self._password,
                               netloc.rpartition('@')[2])
        return urlunparse((scheme, netloc, path, params, query, fragment))

    # -------------------------------------------------------------------------
    def _log_path(self, path, filename='.'):
        """Return normalized full path of file or ``None``.

        :param path: (string)
            Relative path to file.
        :param filename: (string, optional)
            Name of file.
        :return: (string or ``None``)
            Normalized full path or ``None`` if the file is not eligible.
        """
        if filename in EXCLUDED_FILES:
            return
        filename = normpath(join(self.path, path, filename))
        if not filename.startswith(self.path) or not exists(filename):
            return
        return filename.encode('utf8')


# =============================================================================
class VcsNone(Vcs):
    """No Version Control System."""

    engine = 'none'

    # -------------------------------------------------------------------------
    def clone(self, handler=None):
        """Create a directory.

        See abstract function :meth:`~.lib.vcs.Vcs.clone`.
        """
        if not exists(self.path):
            makedirs(self.path)

    # -------------------------------------------------------------------------
    def pull_update(self, handler):
        """Do nothing.

        See abstract function :meth:`~.lib.vcs.Vcs.pull_update`.
        """
        pass

    # -------------------------------------------------------------------------
    def commit_push(self, message, user_id, password, name, handler):
        """Do nothing.

        See abstract function :meth:`~.lib.vcs.Vcs.commit_push`.
        """
        pass

    # -------------------------------------------------------------------------
    def revert_all(self, handler):
        """Do nothing.

        See abstract function :meth:`~.lib.vcs.Vcs.revert_all`.
        """
        pass

    # -------------------------------------------------------------------------
    def backout(self, name, handler):
        """Do nothing.

        See :meth:`~.lib.vcs.Vcs.backout`.
        """
        pass

    # -------------------------------------------------------------------------
    def recover(self, handler):
        """Do nothing.

        See :meth:`~.lib.vcs.Vcs.recover`.
        """
        pass

    # -------------------------------------------------------------------------
    def last_change(self):
        """Return the last change on the repository.

        See :meth:`~.lib.vcs.Vcs.last_change`.
        """
        return datetime.fromtimestamp(getmtime(self.path)), '-', '-'

    # -------------------------------------------------------------------------
    def log(self, path, filename, limit=1):
        """show revision history of file ``filename``.

        See :meth:`~.lib.vcs.Vcs.log`.
        """
        try:
            return ((datetime.fromtimestamp(
                getmtime(self.full_path(path, filename))), '-', '-', '-'),)
        except OSError:
            return

    # -------------------------------------------------------------------------
    def add(self, path, handler):
        """Do nothing.

        See abstract function :meth:`~.lib.vcs.Vcs.add`.
        """
        pass

    # -------------------------------------------------------------------------
    def rename(self, path, filename, new_name, handler):
        """Rename a file.

        See :meth:`~.lib.vcs.Vcs.rename`.
        """
        new_name = self.full_path(path, new_name)
        if isinstance(new_name, TranslationString):
            return handler.report('error', new_name)
        filename = self.full_path(path, filename)
        if isinstance(filename, TranslationString):
            return handler.report('error', filename)
        if exists(new_name):
            return handler.report('error', _('File already exists!'))
        try:
            renames(filename, new_name)
        except OSError as error:
            return handler.report('error', error)

    # -------------------------------------------------------------------------
    def remove(self, path, filename, handler):
        """Remove a file.

        See :meth:`~.lib.vcs.Vcs.remove`.
        """
        filename = self.full_path(path, filename)
        if isinstance(filename, TranslationString):
            return handler.report('error', filename)
        if exists(filename):
            if isfile(filename):
                remove(filename)
            else:
                rmtree(filename)

    # -------------------------------------------------------------------------
    def revision(self, fullname, revision):
        """Retrieve a revision.

        See :meth:`~.lib.vcs.Vcs.revision`.
        """
        with open(fullname, 'rb') as hdl:
            content = hdl.read()
        return content

    # -------------------------------------------------------------------------
    def diff(self, fullname, revision):
        """Return differences between revision ``revision`` and current
        revision.

        See :meth:`~.lib.vcs.Vcs.diff`.
        """
        return ''
