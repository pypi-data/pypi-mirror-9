# $Id: handler.py 7981fd623a54 2015/02/21 08:15:22 Patrick $
"""A *handler* manages access to a storage and its indexing."""

import logging
from os import listdir, walk, makedirs, remove
from os.path import join, exists, splitext, relpath, isdir
from os.path import basename, getmtime
from shutil import rmtree
from time import time, sleep
from threading import Thread
from locale import strxfrm
from lxml import etree
import re
from whoosh.index import exists_in, create_in, open_dir, LockError
from whoosh.fields import Schema, ID, STORED, TEXT, NUMERIC, DATETIME
from whoosh.fields import UnknownFieldError
from whoosh.qparser import QueryParser, MultifieldParser
from subprocess import Popen, PIPE, STDOUT

from .utils import _, EXCLUDED_FILES, decrypt, unzip
from .utils import normalize_spaces, age, size_label, cache_decorator
from .utils import settings_get_list
from .xml import load
from .vcs import VcsNone
from .vcs.hg import VcsMercurial, VcsLocal
from .vcs.hgsvn import VcsHgSubversion
from .vcs.svn import VcsSubversion
from ..models import DBSession
from ..models.indexers import Indexer, IndexerExtractor
from ..models.storages import Storage


LOG = logging.getLogger(__name__)


# =============================================================================
class HandlerManager(object):
    """This class manages all handlers.

    One instance of :class:`HandlerManager` is created during application
    initialization. It is only used in front mode. It is stored in application
    registry.

    ``self.cache_manager`` is a :class:`beaker.cache.CacheManager` instance.

    ``self._indexers`` is a dictionary such as
    ``{indexer_id: (value_type, extrators),...}`` where ``extractors``
    is a tuple like ``(indexed_files_regex, extractor_type, parameter)``.

    ``self._handlers`` is a dictionary of :class:`Handler` objects.
    """

    # -------------------------------------------------------------------------
    def __init__(self, settings, cache_manager):
        """Constructor method.

        :param settings: (dictionary)
            Setting dictionary.
        :param cache_manager: (:class:`beaker.cache.CacheManager` instance)
            Global Beaker cache manager.
        """
        # Attributes
        self.settings = settings
        self.cache_manager = cache_manager
        self._indexers = None
        self._handlers = {}
        self._thread = None

        # VCS engine classes
        vcs_classes = {'none': VcsNone, 'local': VcsLocal, 'hg': VcsMercurial,
                       'hgsvn': VcsHgSubversion, 'svn': VcsSubversion}
        self.vcs_classes = {}
        for vcs in settings_get_list(settings, 'storage.vcs'):
            if vcs in vcs_classes and vcs not in self.vcs_classes:
                self.vcs_classes[vcs] = vcs_classes[vcs]

    # -------------------------------------------------------------------------
    def vcs_list(self):
        """Return a list of available Version Control System."""
        return self.vcs_classes.keys()

    # -------------------------------------------------------------------------
    def get_handler(self, storage_id, storage=None):
        """Create or retrieve a Storage Control System for storage
        ``storage``.

        :param storage_id: (string)
            Storage ID.
        :param storage: (:class:`~.models.storages.Storage` instance,
            optional).
        :return: (:class:`Handler` instance or ``None``)
        """
        self._cleanup()
        if storage_id in self._handlers:
            self._handlers[storage_id].expire = \
                time() + self._handlers[storage_id].cache.expiretime
            return self._handlers[storage_id]

        if storage is None or storage_id != storage.storage_id \
                or storage.vcs_engine not in self.vcs_classes:
            return

        self._handlers[storage_id] = Handler(self, storage)
        return self._handlers[storage_id]

    # -------------------------------------------------------------------------
    def remove_handler(self, storage_id):
        """Remove handler from handler list.

        :param storage_id: (string)
            Storage ID.
        """
        if storage_id in self._handlers:
            del self._handlers[storage_id]

    # -------------------------------------------------------------------------
    def progress(self, storage_ids, pending=False):
        """Return the progress of actions on storages.

        :param storage_ids: (list)
            Storage ID list.
        :param pending: (boolean, default=False)
            ``True`` if there is a pending work.
        :return: (tuple)
            Return a tuple such as ``(working, progress_list)``.

        ``working`` is a boolean indicating whether one of the storage is in
        progress. ``progress_list`` is a list of items like ``(status,
        message)``. See :class:`Handler` class.
        """
        working = False
        prgrss = {}
        for storage_id in storage_ids:
            if storage_id in self._handlers:
                handler_prgrss = self._handlers[storage_id].progress()
                if handler_prgrss[0] != 'wait':
                    prgrss[storage_id] = handler_prgrss
                    working |= handler_prgrss[0] == 'run'
        return working | pending, prgrss

    # -------------------------------------------------------------------------
    def index(self, storage_id, in_thread=False):
        """Index storage ``storage_id`` directly or in a thread.

        :param storage_id: (string)
            ID of storage to index.
        :param in_thread: (boolean, default=False)
            Launch indexing in a thread or not.
        """
        # Nothing to do
        if not self._handlers[storage_id].indexing[0]:
            return
        if self._handlers[storage_id].indexing[0] != 'ok' \
                and self._handlers[storage_id].indexing[0][0:6] != 'update':
            self._handlers[storage_id].indexing[0] += '>update'
            return

        # Directly...
        if not in_thread:
            self._thread_index(storage_id)
            return

        # ...or in a thread
        if self._thread is not None and self._thread.is_alive():
            return
        if self._thread is not None:
            del self._thread
        self._thread = Thread(
            target=self._thread_index, name='index:%s' % storage_id,
            args=[storage_id])
        self._thread.start()
        self._handlers[storage_id].expire = \
            time() + self._handlers[storage_id].cache.expiretime

    # -------------------------------------------------------------------------
    def delete_index(self, update=True):
        """Delete all indexes.

        :param update: (boolean, default=True)
            If ``True`` update indexes after deleting.
        """
        # Index directory
        index_dir = self.settings.get('storage.index')
        if index_dir is None or not exists(index_dir):
            return

        # Is something running?
        running = False
        for storage_id in self._handlers:
            if self._handlers[storage_id].indexing[0][0:3] == 'run':
                self._handlers[storage_id].indexing[0] = 'run>delete'
                running = True
            elif self._handlers[storage_id].indexing[0]:
                self._handlers[storage_id].indexing[0] = 'delete'
        if running:
            return

        # Delete indexes
        LOG.info('Deleting indexes')
        self._remove_index_directory(index_dir)
        self._indexers = None

        # Update indexes
        if update:
            for storage in DBSession.query(Storage):
                if storage.storage_id not in self._handlers \
                        and storage.indexed_files:
                    self._handlers[storage.storage_id] = Handler(self, storage)
                if storage.storage_id in self._handlers \
                        and self._handlers[storage.storage_id].indexing[0]:
                    self._handlers[storage.storage_id].indexing[0] = 'update'
                    self._handlers[storage.storage_id].indexing[1] = 0
        self._cleanup()

    # -------------------------------------------------------------------------
    def search(self, storage_id, fieldnames, query, limit=20):
        """Search in storage ``storage_id``.

        :param storage_id: (string)
            ID of storage to search.
        :param filednames: (list)
            List of fields to search.
        :param query: (string)
            A query in the Whoosh default query language.
        :param limit: (integer, default=20)
            Maximum number of results.
        :return: (list of lists)
            A list such as ``[[score, None, storage_id, title, extract],...]``.
        """
        # Nothing to do
        index_dir = self.settings['storage.index']
        if not exists(index_dir) \
                or not exists_in(index_dir, indexname=storage_id):
            return []

        # Update storage
        if storage_id not in self._handlers:
            handler = self.get_handler(
                storage_id, DBSession.query(Storage)
                .filter_by(storage_id=storage_id).first())
        else:
            handler = self.get_handler(storage_id)
        handler.synchronize(None)

        # Query
        # pylint: disable = locally-disabled, W0703
        result_list = []
        index = open_dir(index_dir, indexname=storage_id)
        with index.searcher() as searcher:
            if len(fieldnames) == 1:
                parser = QueryParser(fieldnames[0], index.schema)
            else:
                parser = MultifieldParser(fieldnames, index.schema)
            try:
                results = searcher.search(parser.parse(query), limit=limit)
            except Exception:
                index.close()
                return result_list

            for hit in results:
                result_list.append([
                    round(hit.score, 2), None, storage_id,
                    hit['path'].partition('#')[0], hit.get('title'),
                    hit.get('extract')])

        index.close()
        return result_list

    # -------------------------------------------------------------------------
    def _cleanup(self):
        """Delete expired Handler and launch indexing."""
        # Delete expired and find pending operations
        now = time()
        indexing = False
        waiting = []
        for storage_id in self._handlers.keys():
            handler = self._handlers[storage_id]
            if handler.expire < now:
                if handler.progress()[0] != 'run' \
                        and handler.indexing[0] in ('', 'ok'):
                    del self._handlers[storage_id]
                continue
            if handler.indexing[0][0:3] == 'run':
                indexing = True
            elif handler.indexing[0] not in ('', 'ok') \
                    and handler.indexing[1] < now:
                if handler.progress()[0] == 'run':
                    handler.indexing[1] = now + handler.indexing[2]
                else:
                    waiting.append([storage_id] + handler.indexing[0:2])

        # Indexing
        if indexing or not waiting:
            return
        waiting = sorted(waiting, key=lambda item: item[2])
        if waiting[0][1][0:6] == 'delete':
            self.delete_index()
        else:
            self.index(waiting[0][0], True)

    # -------------------------------------------------------------------------
    def _thread_index(self, storage_id):
        """Action launched in a thread to index a storage.

        :param storage_id: (string)
            ID of storage to index.
        """
        try:
            index = self._open_or_create_index(storage_id)
            writer = index.writer()
        except LockError:
            return
        self._handlers[storage_id].indexing[0] = 'run%s%s' \
            % self._handlers[storage_id].indexing[0].partition('>')[1:]
        done = set()
        root = join(self.settings['storage.root'], storage_id)
        LOG.info('Indexing %s', storage_id)

        # Loop over the stored documents
        for docnum, fields in writer.reader().iter_docs():
            name = join(root, fields['path']).partition('#')[0]
            if not exists(name) or getmtime(name) > fields['time']:
                writer.delete_document(docnum)
            else:
                done.add(fields['path'])

        # Loop over the files
        indexed_files = self._handlers[storage_id].indexing[3]
        for path, dirs, files in walk(root):
            for name in dirs:
                if name in EXCLUDED_FILES or '~' in name:
                    dirs.remove(name)
            for name in files:
                if indexed_files.search(name) and name not in EXCLUDED_FILES:
                    name = relpath(join(path, name), root)
                    if not isinstance(name, unicode):
                        name = name.decode('utf8')
                    if name not in done:
                        self._add_document_index(writer, storage_id, name)

        writer.commit()
        index.close()
        DBSession.close()
        self._handlers[storage_id].indexing[0] = \
            self._handlers[storage_id].indexing[0].partition('>')[2] or 'ok'

    # -------------------------------------------------------------------------
    def _open_or_create_index(self, storage_id):
        """Open and index structure (eventually create it).

        :param storage_id: (string)
            ID of index to open.
        :return: (:class:`whoosh.index.Index` instance)
        """
        # Open existing index
        index_dir = self.settings['storage.index']
        if exists(index_dir) and exists_in(index_dir, indexname=storage_id):
            return open_dir(index_dir, indexname=storage_id)

        # Create schema
        schema = Schema(
            path=ID(unique=True, stored=True, sortable=True), time=STORED,
            title=TEXT(stored=True, sortable=True), extract=TEXT(stored=True),
            filename=ID)
        done = set((u'path', u'time', u'title', u'extract', u'filename'))
        for indexer in DBSession.query(Indexer.indexer_id, Indexer.value_type):
            if indexer[0] not in done:
                if indexer[1] == 'integer':
                    schema.add(indexer[0], NUMERIC)
                elif indexer[1] == 'date':
                    schema.add(indexer[0], DATETIME)
                else:
                    schema.add(indexer[0], TEXT)
                done.add(indexer[0])

        # Create index
        if not exists(index_dir):
            makedirs(index_dir)
        return create_in(index_dir, schema, indexname=storage_id)

    # -------------------------------------------------------------------------
    def _add_document_index(self, writer, storage_id, path):
        """Add a document to the index.

        :param writer: (:class:`whoosh.writing.IndexWriter` instance)
            Writer on current index.
        :param storage_id: (string)
            ID of storage to index.
        :param path: (string)
            Relative path to file to add.
        """
        # Index document
        # pylint: disable = locally-disabled, E1103
        content = tree = None
        name = basename(path)
        fields = {'path': path, 'time': time(), 'filename': name}
        self._load_indexers()
        for indexer_id in self._indexers:
            chunks = []
            for extractor in self._indexers[indexer_id][1]:
                if not extractor[0].search(name):
                    continue
                if extractor[1] == 'xpath':
                    if tree is None:
                        tree = load(join(
                            self.settings['storage.root'], storage_id, path))
                    self._index_xpath(tree, extractor[2], extractor[3], chunks)
                elif extractor[1] == 'iim':
                    self._index_iim(
                        join(self.settings['storage.root'], storage_id, path),
                        extractor[2].split(), extractor[3], chunks)
                else:
                    if content is None:
                        with open(join(self.settings['storage.root'],
                                       storage_id, path), 'r') as hdl:
                            content = hdl.read()
                    self._index_regex(
                        content, extractor[2], extractor[3], chunks)
            chunks = self._format_index_field(indexer_id, chunks)
            if chunks:
                fields[indexer_id] = chunks

        # pylint: disable = locally-disabled, W0142
        try:
            writer.add_document(**fields)
        except (ValueError, UnknownFieldError) as error:
            LOG.error('%s/%s: %s', storage_id, path, error)

    # -------------------------------------------------------------------------
    def _load_indexers(self, reset=False):
        """Fill indexer dictionary."""
        # Something to do?
        if not reset and self._indexers is not None:
            return

        # Load from database
        self._indexers = {}
        for extractor in DBSession.query(
                IndexerExtractor.indexer_id, Indexer.value_type,
                IndexerExtractor.indexed_files,
                IndexerExtractor.extractor_type, IndexerExtractor.parameter,
                IndexerExtractor.limit)\
                .join(Indexer).order_by(IndexerExtractor.indexer_id):
            indexer_id = extractor[0]
            value_type = extractor[1]
            try:
                extractor = (
                    re.compile(extractor[2]), extractor[3],
                    extractor[3] == 'regex' and re.compile(extractor[4]) or
                    extractor[4], extractor[5])
            except re.error as error:
                LOG.error('Indexer "%s": %s', indexer_id, error)
                continue
            if indexer_id in self._indexers:
                self._indexers[indexer_id][1].append(extractor)
            else:
                self._indexers[indexer_id] = (value_type, [extractor])

    # -------------------------------------------------------------------------
    @classmethod
    def _index_regex(cls, content, regex, limit, chunks):
        """Extract text from ``content`` according to ``regex``.

        :param content: (string)
            Content to process.
        :param regex: (:class:`re.RegexObject` instance)
            Regular expression to use.
        :param limit: (integer or ``None``)
            Maximum size of the extraction.
        :param chunks: (list)
            List of chunks to complete.
        """
        if not regex.pattern or regex.pattern == '.*':
            chunks.append(content.decode('utf8'))
        else:
            chunks.append(u' '.join(regex.findall(content)))
        if limit:
            chunks[-1] = normalize_spaces(chunks[-1])[0:limit]

    # -------------------------------------------------------------------------
    @classmethod
    def _index_iim(cls, filename, fields, limit, chunks):
        """Extract IIM (Information Interchange Model) fields from image
        ``filename``.

        :param filename: (string)
            Full path to image.
        :param fields: (list)
            Fields to extract.
        :param limit: (integer or ``None``)
            Maximum size of the extraction.
        :param chunks: (list)
            List of chunks to complete.
        """
        cmd = ['exiv2', '-pa']
        for field in fields:
            cmd += ['-g', field]
        process = Popen(cmd + [filename], stderr=STDOUT, stdout=PIPE)
        try:
            output = process.communicate()[0]
        except OSError:
            return

        chunk = u''
        for line in output.split('\n'):
            line = line[59:].decode('latin-1')
            if line not in chunk:
                chunk += line
        chunks.append(normalize_spaces(chunk))
        if limit:
            chunks[-1] = chunks[-1][0:limit]

    # -------------------------------------------------------------------------
    @classmethod
    def _index_xpath(cls, tree, xpath, limit, chunks):
        """Extract text from ``content`` according to ``regex``.

        :param tree: (:class:`ElementTree`)
            Content to process.
        :param xpath: (string)
            XPath to use.
        :param limit: (integer or ``None``)
            Maximum size of the extraction.
        :param chunks: (list)
            List of chunks to complete.
        """
        if isinstance(tree, basestring):
            return

        try:
            elements = tree.xpath(xpath)
        except etree.XPathEvalError, error:
            LOG.error('XPath "%s": %s', xpath, error)
            return
        if not elements:
            return

        if isinstance(elements, basestring):
            chunks.append(elements)
        elif isinstance(elements[0], basestring):
            elements = [k for k in elements if k.strip()]
            chunks.append(u' '.join(elements))
        else:
            elements = [
                isinstance(k.text, unicode) and k.text or k.text.encode('utf8')
                for k in elements if k.text]
            chunks.append(u' '.join(elements))
        if limit:
            chunks[-1] = normalize_spaces(chunks[-1])[0:limit]

    # -------------------------------------------------------------------------
    def _format_index_field(self, indexer_id, chunks):
        """Format index field according to type.

        :param indexer: (string)
            Indexer ID.
        :param chunks: (list)
            Content of field to format.
        :return: (string)
        """
        if indexer_id == 'title':
            return normalize_spaces(u' '.join(chunks))

        if self._indexers[indexer_id][0] == 'date' and chunks:
            chunks = chunks[0].isdigit() and u'%04d' % int(chunks[0]) \
                or chunks[0].strip()
            # pylint: disable = locally-disabled, W0702
            try:
                DATETIME().to_bytes(chunks)
            except:
                return ''
            return chunks

        return u' '.join(chunks).strip()

    # -------------------------------------------------------------------------
    def _remove_index_directory(self, index_dir):
        """Remove index directory.

        :param index_dir: (string)
            Absolute path to index directory.
        """
        for storage_id in self._handlers:
            if self._handlers[storage_id].indexing[0]:
                self._handlers[storage_id].indexing[0] = 'run'

        for filename in listdir(index_dir):
            filename = join(index_dir, filename)
            if isdir(filename):
                rmtree(filename)
            else:
                remove(filename)


# =============================================================================
class Handler(object):
    """This class manages access to one storage.

    ``self.uid`` is the ID of the associated storage.

    ``self.expire`` is the deadline for this object.

    ``self.cache`` is a :class:`beaker.cache.Cache` instance.

    ``self.vcs`` is a :class:`~.lib.vcs.Vcs` instance.

    ``self.indexing`` is the indexing status of the storage in a tuple such as
    ``(status, start_time, delay_to_start, indexed_file_regex)``:

    * ``''``: no index
    * ``'ok'``: no pending indexing operation
    * ``'update'``: waiting for indexing
    * ``'delete'``: waiting for deleting index
    * ``'run'``: in progress

    ``run`` status can be completed by next step: ``run>delete>index``.

    ``self._report`` is a tuple such as ``(status, message, expire, ttl)``
    where ``expire`` is the report validity date and ``status`` is one of the
    following strings:

    * ``'wait'``: waiting for VCS operation
    * ``'run'``: VCS operation in progress
    * ``'error'``: VCS operation ended with error
    * ``'end'``: VCS operation ended with success

    ``self._refresh`` is a tuple such as ``(time_to_refresh, refresh_period)``.
    """
    # pylint: disable = locally-disabled, R0902

    # -------------------------------------------------------------------------
    def __init__(self, handler_manager, storage):
        """Constructor method.

        :param handler_manager: (:class:`HandlerManager` instance)
            Application :class:`HandlerManager` object.
        :param storage: (:class:`~.models.storages.Storage` instance).
        """
        self.uid = storage.storage_id
        self.cache = handler_manager.cache_manager.get_cache(
            'stg_%s' % self.uid,
            expire=int(handler_manager.settings.get('storage.cache', 3600)))
        self.expire = time() + self.cache.expiretime
        self.vcs = handler_manager.vcs_classes[storage.vcs_engine](
            join(handler_manager.settings['storage.root'], self.uid),
            storage.vcs_url, storage.vcs_user, decrypt(
                storage.vcs_password,
                handler_manager.settings.get('encryption', '-')))
        is_indexing = storage.indexed_files \
            and 'storage.index' in handler_manager.settings
        try:
            self.indexing = [
                is_indexing and 'ok' or '', 0,
                int(handler_manager.settings.get('refresh.short', 2)),
                is_indexing and re.compile(storage.indexed_files)]
        except re.error as error:
            LOG.error('Indexed files for storage "%s": %s', self.uid, error)
            self.indexing = ['', 0, 0, None]
        self._report = (
            'wait', None, 0,
            int(handler_manager.settings.get('storage.report_ttl', 120)))
        self._refresh = [0, int(storage.refresh)]
        self._thread = None

    # -------------------------------------------------------------------------
    def clone(self, request=None):
        """Launch an action to clone a storage.

        :param request: (:class:`pyramid.request.Request` instance, optional)
            Current request.
        """
        # Action directly...
        if request is None:
            self.index()
            return self.vcs.clone()

        # ...or in a thread
        if self.launch(request, self.vcs.clone):
            self.index()
            self._refresh[0] = time() + self._refresh[1]

    # -------------------------------------------------------------------------
    def synchronize(self, request, force=False):
        """Launch an action to synchronize storage with its source.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param force: (boolean, default=False)
            Force synchronization even if period is not over.
        :return: (boolean)
            ``True`` if it really launch a synchronization.

        If ``force`` is ``False``, the synchronizaton is only done if the
        delay of ``synchro_period`` seconds has expired.
        """
        # Something to do?
        if not force and self._refresh[0] > time():
            self.expire = time() + self.cache.expiretime
            return False

        # Directly...
        if request is None:
            self.report('run')
            error = self.vcs.pull_update(self)
            if error:
                self.report('error', error)
                return False
            self._refresh[0] = time() + self._refresh[1]
            self.report('end')
            self.index()
            return True

        # ...or in a thread
        if self.launch(request, self.vcs.pull_update):
            self._refresh[0] = time() + self._refresh[1]
            self.index()
            return True
        return False

    # -------------------------------------------------------------------------
    def report(self, status, message=None):
        """Save a report.

        :param status: (string)
            Current status. See :class:`Handler` class.
        :param message: (string, optional)
            Message to write in report.
        :return: (string or ``None``)
            Message.
        """
        self._report = (
            status, message, time() + self._report[3], self._report[3])
        self.expire = time() + self.cache.expiretime
        return message

    # -------------------------------------------------------------------------
    def progress(self):
        """Return the progress of action on the storage.

        :return: (tuple)
            A tuple such as ``(status, message)``. See :class:`Handler` class.
        """
        if self._thread is not None and self._thread.is_alive():
            return ('run', None)
        if self._report[0] != 'wait' and self._report[2] < time():
            self.report('wait')
        return self._report[0:2]

    # -------------------------------------------------------------------------
    @cache_decorator()
    def dir_infos(self, path, sort, quick):
        """List all files of a directory with VCS informations.

        :param path: (string)
            Relative path of the directory.
        :param sort: (string)
            A sort order among ``+name``, ``-name``, ``+size``, ``-size``,
            ``+date``, ``-date``.
        :param quick: (boolean)
            ``True`` to have a quick information.
        :return: (tuple)
            A tuple such as ``(dirs, files)`` where ``dirs`` and ``files`` are
            lists such as ``[name, type, size, date, revision, user,
            message]``. For instance: ``['README', 'plain', '45.7 Kio',
            '2 days', '16:0e0229a916f4', 'user1', 'Bug fixed']``.
        """
        status = self._report[0]
        self.report('run')

        # Get information
        dirs, files = self.vcs.directory_log(path, quick)

        # Sort
        key = {'size': lambda k: k[2], 'date': lambda k: k[3]}.get(
            sort[1:], lambda k: strxfrm(k[0].encode('utf8')))
        dirs = sorted(dirs, key=key, reverse=(sort[0] == '-'))
        files = sorted(files, key=key, reverse=(sort[0] == '-'))

        # Improve labels
        for item in dirs:
            item[2] = size_label(item[2], True)
            item[3] = (age(item[3]), item[3].isoformat(' ').partition('.')[0])
        for item in files:
            item[2] = size_label(item[2], False)
            item[3] = (age(item[3]), item[3].isoformat(' ').partition('.')[0])

        if status != 'run':
            self.report('wait')
        return dirs, files

    # -------------------------------------------------------------------------
    def upload(self, user, path, upload_file, filename, message):
        """Synchronize, upload files and propagate.

        :param user: (list)
            VCS user like ``(user_id, password, user_name)``.
        :param path: (string)
            Relative path to files.
        :param upload_file: (:class:`cgi.FieldStorage` instance)
            FieldStorage of the file to upload.
        :param filename: (string or `None``)
            Name of file to upload or ``None``.
        :param message: (string)
            Commit message.
        """
        # Check filename
        upload_filename = upload_file.filename
        if '\\' in upload_filename:
            upload_filename = upload_filename.split('\\')[-1]
        if filename is not None and filename != upload_filename:
            self.report('error', _('File names are different.'))
            return

        # Check repository
        if not self._check_repository(user, message):
            return

        # Upload files
        fullpath = join(self.vcs.path, path or '.')
        if not exists(fullpath):
            return
        ext = splitext(upload_file.filename)[1]
        if ext != '.zip' or filename:
            filename = filename or upload_filename
            with open(join(fullpath, filename), 'w') as hdl:
                hdl.write(upload_file.file.read())
        else:
            unzip(upload_file.file, fullpath)
            upload_file.file.close()

        # Add
        if self.vcs.add(path, self):
            return

        # Propagate
        self._propagate(user, message)

    # -------------------------------------------------------------------------
    def create(self, user, seed, path, name, message):
        """Create a new file according to the seed file.

        :param user: (list)
            VCS user like ``(user_id, password, user_name)``.
        :param seed: (string)
            Full path to the seed file.
        :param path: (string)
            Relative path to file to create.
        :param name: (string)
            Name of the file to create.
        :param message: (string)
            Commit message.
        """
        # Check repository
        if not self._check_repository(user, message):
            return

        # Create file
        if self.vcs.create(seed, path, name, self):
            return

        # Propagate
        self._propagate(user, message)

    # -------------------------------------------------------------------------
    def duplicate(self, user, path, original, name, message):
        """Duplicate the ``original`` file.

        :param user: (list)
            VCS user like ``(user_id, password, user_name)``.
        :param path: (string)
            Relative path to file to create.
        :param original: (string)
            Name of the original file.
        :param name: (string)
            Name of the file to create.
        :param message: (string)
            Commit message.
        """
        # Check repository
        if not self._check_repository(user, message):
            return

        # Duplicate file
        if self.vcs.duplicate(path, original, name, self):
            return

        # Propagate
        self._propagate(user, message)

    # -------------------------------------------------------------------------
    def mkdir(self, user, path, name, message):
        """Make a directory.

        :param user: (list)
            VCS user like ``(user_id, password, user_name)``.
        :param path: (string)
            Relative path to directory to create.
        :param name: (string)
            Name of directory to create.
        :param message: (string)
            Commit message.
        """
        # Check repository
        if self.vcs.engine == 'svn' \
                and not self._check_repository(user, message):
            return

        # Make directory
        if self.vcs.mkdir(path, name, self):
            return

        # Propagate
        if self.vcs.engine == 'svn':
            self._propagate(user, message)
        else:
            self.report('end')

    # -------------------------------------------------------------------------
    def add(self, user, path, message):
        """Synchronize, add files and propagate.

        :param user: (list)
            VCS user like ``(user_id, password, user_name)``.
        :param path: (string)
            Relative path to files.
        :param message: (string)
            Commit message.
        """
        # Check repository
        if not self._check_repository(user, message):
            return

        # Add
        if self.vcs.add(path, self):
            return

        # Propagate
        self._propagate(user, message)

    # -------------------------------------------------------------------------
    def rename(self, user, path, filename, new_name, message):
        """Synchronize, rename a file and propagate.

        :param user: (list)
            VCS user like ``(user_id, password, user_name)``.
        :param path: (string)
            Relative path to files.
        :param filename: (string)
            Name of file to move.
        :param new_name: (string)
            New name.
        :param message: (string)
            Commit message.
        """
        # Check repository
        if not self._check_repository(user, message):
            return

        # Move files
        if self.vcs.rename(path, filename, new_name, self):
            return

        # Propagate
        self._propagate(user, message)

    # -------------------------------------------------------------------------
    def remove(self, user, path, filenames, message):
        """Synchronize, remove files and propagate.

        :param user: (list)
            VCS user like ``(user_id, password, user_name)``.
        :param path: (string)
            Relative path to files.
        :param filenames: (list)
            Names of files to remove.
        :param message: (string)
            Commit message.
        """
        # Check repository
        if not self._check_repository(user, message):
            return

        # Remove files
        for filename in filenames:
            if self.vcs.remove(path, filename, self):
                return

        # Propagate
        self._propagate(user, message)

    # -------------------------------------------------------------------------
    def replace(self, user, path, content, message):
        """Synchronize, replace one file and propagate.

        :param user: (list)
            VCS user like ``(user_id, password, user_name)``.
        :param path: (string)
            Relative path to files.
        :param content: (string)
            New content of the file to replace.
        """
        # Check repository
        if not self._check_repository(user, message):
            return

        # Does the file exists?
        filename = join(self.vcs.path, path)
        if not exists(filename):
            self.report('error', _('This file does not exist anymore.'))
            return

        # Save file
        with open(filename, 'wb') as hdl:
            hdl.write(content)

        # Propagate
        self._propagate(user, message)

    # -------------------------------------------------------------------------
    def recover(self):
        """Recover from an interrupted commit or pull."""
        self.vcs.recover(self)

    # -------------------------------------------------------------------------
    def index(self):
        """Schedule index."""
        if self.indexing[0] == 'ok':
            self.indexing[0] = 'update'
            self.indexing[1] = time() + self.indexing[2]

    # -------------------------------------------------------------------------
    def launch(self, request, action, args=(), kwargs=None):
        """Launch a new action in a thread.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param action: (function)
            Action to launch.
        :param args: (tuple, optional)
            Arguments for the action.
        :param kwargs: (dictionary, optional)
            Keyword arguments for the action.
        :return: (boolean)
            ``True`` if action has been launched.

        Only one action per storage at a time is possible.
        """
        # Is this storage undergoing an action?
        if self._thread is not None and self._thread.is_alive():
            request.session.flash(_(
                '${i}: action already in progress.', {'i': self.uid}), 'alert')
            return False
        if self._thread is not None:
            del self._thread

        # Launch action
        kwargs = kwargs or {}
        if action.im_self is not self:
            kwargs['handler'] = self
        self._thread = Thread(
            target=action, name='vcs:%s' % self.uid, args=args, kwargs=kwargs)
        self._thread.start()
        self.expire = time() + self.cache.expiretime
        return True

    # -------------------------------------------------------------------------
    def _check_repository(self, user, message):
        """Wait for repository availability, synchronize and check push
        capacity.

        :param user: (list)
            VCS user like ``(user_id, password, user_name)``.
        :param message: (string)
            Commit message.
        :return: (boolean)
        """
        k = 10
        while self._report[0] == 'run' and k:
            k -= 1
            sleep(1)
        if self._report[0] == 'run':
            self.report('error', _('Storage is busy.'))
            return False

        if self.synchronize(None, True) and \
           not self.vcs.commit_push(message, user[0], user[1], user[2], self):
            return True

        self.vcs.revert_all(self)
        return False

    # -------------------------------------------------------------------------
    def _propagate(self, user, message):
        """Commit and push chages or revert all.

        :param user: (list)
            VCS user like ``(user_id, password, user_name)``.
        :param message: (string)
            Commit message.
        """
        if not self.vcs.commit_push(message, user[0], user[1], user[2], self):
            self.report('end')
        else:
            self.vcs.backout(user[2] or user[0], self)
