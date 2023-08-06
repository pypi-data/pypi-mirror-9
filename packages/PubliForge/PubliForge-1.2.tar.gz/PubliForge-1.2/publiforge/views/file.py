# $Id: file.py 7981fd623a54 2015/02/21 08:15:22 Patrick $
# pylint: disable = locally-disabled, no-name-in-module
"""File view callables."""

from os.path import join, exists, isdir, splitext, dirname, relpath
from time import time, sleep
from colander import Mapping, SchemaNode, String, Boolean, Integer, OneOf
from colander import Length
from pygments import highlight
from pygments.lexers import get_lexer_for_filename, XmlLexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound
from webhelpers2.html import literal

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPForbidden
from pyramid.response import Response
from pyramid.i18n import get_localizer

from ..lib.utils import _, MIME_TYPES, get_mime_type, age
from ..lib.viewutils import get_action, current_storage, file_download
from ..lib.viewutils import add2container, query_storages
from ..lib.viewutils import vcs_user, save_vcs_user
from ..lib.packutils import create_pack
from ..lib.form import Form
from ..lib.widget import Paging
from ..models import NULL, ID_LEN, DESCRIPTION_LEN, PATH_LEN
from ..models import DBSession, close_dbsession
from ..models.storages import Storage
from ..models.indexers import Indexer


SEARCH_LIMIT = (10, 20, 40, 80, 160, 320, 640, 1280, 2560, 5120)


# =============================================================================
class FileView(object):
    """Class to manage files in a storage."""

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        request.add_finished_callback(close_dbsession)
        self._request = request

    # -------------------------------------------------------------------------
    @view_config(
        route_name='file_search', renderer='../Templates/fil_search.pt',
        permission='stg.read')
    def search(self):
        """Search file in storages.

        ``session['search']`` is a dictionary such as ``{'i': indexes, 'q':
        query, 's': scope, 'l': limit, 'r': results}``.
        :meth:`_search_indexes` initializes this tuple and fills ``indexes``.
        :meth:`_search` fills ``query``, ``scope``, ``limit`` and ``result``.
        """
        # Query & scope
        fields, values = self._search_indexes()
        scope, storage_ids = self._search_scope()

        # Form and action
        session = self._request.session
        form = self._search_form(storage_ids)
        action, items = get_action(self._request)
        if action[0:4] == 'dnl!':
            name = len(items) > 1 and _('search_${t}.zip', {'t': int(time())})
            return file_download(
                self._request, self._request.registry.settings['storage.root'],
                items, name and get_localizer(self._request).translate(name))
        elif action == 'cls!' and 'container' in session:
            del session['container']
        elif action[0:4] in ('pck!', 'prc!'):
            add2container(self._request, action[0:3], action[4:7], '.', items)
            form.forget('#')
        elif action[0:4] == 'npk!' and 'project' in session:
            items = create_pack(self._request, items)
            if items[0] is not None:
                return HTTPFound(self._request.route_path(
                    'pack_edit', project_id=items[0], pack_id=items[1],
                    _anchor='tab0'))

        # Results
        results = None
        if 'go' in self._request.params and form.validate():
            results = self._search_query(fields, form.values)
        elif 'search' in session and \
                ('q0index' not in self._request.params or
                 action[0:4] in ('pck!', 'prc!', 'cls!') or
                 self._request.session.peek_flash('alert')):
            results = session['search']['r']
        qindex = [
            self._request.params.get('q0index') or form.values.get('q0index'),
            self._request.params.get('q1index') or form.values.get('q1index')]

        self._request.breadcrumbs.add(_('Advanced search'))
        return {
            'form': form, 'fields': fields, 'values': values, 'scope': scope,
            'qindex': qindex, 'MIME_TYPES': MIME_TYPES,
            'SEARCH_LIMIT': SEARCH_LIMIT, 'results': results}

    # -------------------------------------------------------------------------
    @view_config(
        route_name='file_read', renderer='../Templates/fil_display.pt',
        permission='stg.read')
    @view_config(
        route_name='file_render', renderer='../Templates/fil_display.pt',
        permission='stg.read')
    def display(self):
        """Display content or rendering."""
        storage, handler = current_storage(self._request)
        path, filename, fullname, opener, content = self._file_opener(storage)
        if fullname is None:
            return HTTPFound(self._request.route_path(
                'storage_browse', storage_id=storage['storage_id'], path=path))
        if opener is None:
            return self.download()

        # Action
        form = self._display_form()
        action, items, working = self._display_action(
            form, storage, handler, dirname(path), filename)
        if action == 'npk!' and items[0] is not None:
            return HTTPFound(self._request.route_path(
                'pack_edit', project_id=items[0], pack_id=items[1],
                _anchor='tab0'))
        mode = self._request.registry.settings.get('refresh.short', '2')
        if action == 'dup!':
            sleep(int(mode))
            if not self._request\
                    .registry['handler'].progress((storage['storage_id'],))[0]:
                return HTTPFound(self._request.route_path(
                    'file_render', storage_id=storage['storage_id'],
                    path=join(dirname(path), items[0])))
        working = self._request\
            .registry['handler'].progress((storage['storage_id'],), working)[0]
        if working:
            self._request.response.headerlist.append(('Refresh', mode))

        # Read or render
        mode = self._request.current_route_path().startswith(
            self._request.route_path(
                'file_render', storage_id=storage['storage_id'], path='')) \
            and 'render' or 'read'
        html = ''
        self._pop_read_write_routes(storage)
        if mode == 'render' and opener.can_render():
            html = opener.render(self._request, storage, path, content)
            self._request.breadcrumbs.add(_('File rendering'))
        if not html:
            mode = 'read'
            html = opener.read(self._request, storage, path, content)
            self._request.breadcrumbs.add(_('File content'))

        return {
            'form': form, 'action': action, 'storage': storage, 'path': path,
            'filename': filename, 'mime_type': get_mime_type(fullname),
            'opener': opener, 'mode': mode, 'content': html,
            'position': opener.position(dirname(fullname), filename),
            'searches': self._search_results(storage, path)}

    # -------------------------------------------------------------------------
    @view_config(
        route_name='file_write', renderer='../Templates/fil_modify.pt',
        permission='stg.read')
    @view_config(
        route_name='file_edit', renderer='../Templates/fil_modify.pt',
        permission='stg.read')
    def modify(self):
        """Modify file and save it."""
        storage = current_storage(self._request)[0]
        path, filename, fullname, opener, content = self._file_opener(storage)
        if opener is None or not opener.can_write():
            return HTTPFound(self._request.route_path(
                'file_render', storage_id=storage['storage_id'], path=path))
        if storage['perm'] != 'writer':
            self._request.session.flash(
                _("You can't modify this storage!"), 'alert')
            return HTTPFound(self._request.route_path(
                'file_render', storage_id=storage['storage_id'], path=path))

        # Actions
        preview = description = None
        action = get_action(self._request)[0]
        if action[0:4] == 'des!':
            description = opener.information(self._request, action[4:])
            if self._request.is_xhr:
                return Response(description, content_type='text/html')

        mode = self._request.current_route_path().startswith(
            self._request.route_path(
                'file_edit', storage_id=storage['storage_id'], path='')) \
            and 'edit' or 'write'
        html = ''
        native = None
        self._pop_read_write_routes(storage)
        if (action == 'edt!' or (mode == 'edit' and action != 'wrt!')) \
           and opener.can_edit():
            mode = 'edit'
            form, html, native = opener.edit(
                self._request, action, storage, path, content)
            if html:
                self._request.breadcrumbs.add(_('File editing'))
        if not html:
            mode = 'write'
            form, html, content = opener.write(
                self._request, storage, path, content)
            self._request.breadcrumbs.add(_('File writing'))

        if action == 'pre!' and not self._request.session.peek_flash('alert') \
           and opener.can_render():
            preview = opener.render(
                self._request, storage, path, content, native)

        # Save
        save_vcs_user(self._request, storage)
        if 'vcs_change' not in self._request.params \
                and action == 'sav!' \
                and form.validate() \
                and opener.save(self._request, storage, path,
                                content, form.values):
            self._request.session.flash(_('"${f}" saved.', {'f': path}))
            return HTTPFound(self._request.route_path(
                'file_render', storage_id=storage['storage_id'], path=path))

        return {
            'form': form, 'action': action, 'storage': storage, 'path': path,
            'filename': filename, 'mime_type': get_mime_type(fullname),
            'opener': opener, 'mode': mode, 'content': html,
            'preview': preview, 'description': description}

    # -------------------------------------------------------------------------
    @view_config(route_name='file_media', renderer='json', xhr=True)
    def media(self):
        """Return the URL of the searched media."""
        storage = current_storage(self._request)[0]
        name, opener = self._file_opener(storage)[2:4]
        media_id = self._request.params.get('id')
        name = opener.find_media(
            name, self._request.params.get('type'), media_id)
        if name is None:
            return {'src': ''}
        name = relpath(name, self._request.registry.settings['storage.root'])
        name = self._request.route_path(
            'file_download', storage_id=name.partition('/')[0],
            path=name.partition('/')[2])
        return {'src': name}

    # -------------------------------------------------------------------------
    @view_config(route_name='file_resources_dirs', renderer='json', xhr=True)
    def resources_dirs(self):
        """Return the list of resource directories.
        """
        storage = current_storage(self._request)[0]
        storage_root = self._request.registry.settings['storage.root']
        name, opener = self._file_opener(storage)[2:4]
        dirs = opener.resources_dirs(name, self._request.params.get('type'))
        return {'dirs': [relpath(k, storage_root) for k in dirs]}

    # -------------------------------------------------------------------------
    @view_config(route_name='file_resources_files', renderer='json', xhr=True)
    def resources_files(self):
        """Return the list of media files of a resource directory.
        """
        storage = current_storage(self._request)[0]
        name, opener = self._file_opener(storage)[2:4]
        path = self._request.params.get('path')
        if path[0:2] == './':
            path = join(dirname(name), path[2:])
        else:
            path = join(self._request.registry.settings['storage.root'], path)
        return {'files': opener.resources_files(
            path, self._request.params.get('type'),
            self._request.params.get('all') == 'false')}

    # -------------------------------------------------------------------------
    @view_config(route_name='file_navigate', permission='stg.read')
    def navigate(self):
        """Display the next or previous file of the same type in the same
        directory.
        """
        storage = current_storage(self._request)[0]
        path, filename, fullname, opener = self._file_opener(storage)[0:4]
        if opener is None:
            return HTTPFound(self._request.route_path(
                'file_content', storage_id=storage['storage_id'], path=path))
        new_path = opener.navigate(
            dirname(fullname), filename, self._request.matchdict['direction'])
        if new_path:
            path = relpath(
                new_path, join(
                    self._request.registry.settings['storage.root'],
                    storage['storage_id']))
        else:
            self._request.session.flash(
                _("No more displayable file!"), 'alert')

        return HTTPFound(self._request.route_path(
            'file_render', storage_id=storage['storage_id'], path=path))

    # -------------------------------------------------------------------------
    @view_config(route_name='file_navigate_search', permission='stg.read')
    def navigate_search(self):
        """Display the next or previous file in the search results."""
        storage = current_storage(self._request)[0]
        path = '/'.join(self._request.matchdict['path'])
        files = 'search' in self._request.session \
            and self._request.session['search'].get('r') \
            and [(k[2], k[3]) for k in self._request.session['search']['r']]
        if not files or (storage['storage_id'], path) not in files:
            return HTTPFound(self._request.route_path(
                'file_render', storage_id=storage['storage_id'], path=path))

        if self._request.matchdict['direction'] == 'next':
            files = files[files.index((storage['storage_id'], path)) + 1:]
        else:
            files = files[0:files.index((storage['storage_id'], path))]
            files.reverse()
        for item in files:
            fullname = join(
                self._request.registry.settings['storage.root'],
                item[0], item[1])
            if exists(fullname) and self._request.registry['opener']\
                    .get_opener(fullname, storage)[0]:
                return HTTPFound(self._request.route_path(
                    'file_render', storage_id=item[0], path=item[1]))

        self._request.session.flash(_("No more displayable file!"), 'alert')
        return HTTPFound(self._request.route_path(
            'file_render', storage_id=storage['storage_id'], path=path))

    # -------------------------------------------------------------------------
    @view_config(
        route_name='file_info', renderer='../Templates/fil_info.pt',
        permission='stg.read')
    def info(self):
        """Show file information and VCS log."""
        # pylint: disable = locally-disabled, W0142
        storage, handler = current_storage(self._request)
        path = self._request.matchdict['path']
        fullname = join(handler.vcs.path, *path).encode('utf8')
        filename = path[-1]
        path = '/'.join(path)
        if 'page_size' in self._request.params \
           and self._request.params['page_size'].strip():
            self._request.session['page_size'] = \
                int(self._request.params['page_size'])
        log = handler.vcs.log(
            dirname(path), filename,
            int(self._request.session.get('page_size', 20)))

        content = None
        action = get_action(self._request)[0]
        if action[0:4] == 'shw!':
            action = action[4:]
            content = handler.vcs.revision(fullname, action)
            if content is None:
                self._request.session.flash(
                    _('Unable to retrieve this revision:'
                      ' it was probably moved.'), 'alert')
            else:
                content = {
                    'route': 'file_revision',
                    'revision': action,
                    'file': self._highlight(fullname, content),
                    'label': action != '-' and _(
                        'Revision ${r}', {'r': action}) or ''}
        elif action[0:4] == 'dif!':
            action = action[4:]
            content = handler.vcs.diff(fullname, action)
            content = content.encode('utf8')
            content = {
                'route': 'file_diff',
                'revision': action,
                'file': self._highlight(fullname, content),
                'label': _('Differences with revision ${r}', {'r': action})}

        self._request.breadcrumbs.add(_('File information'))
        return {
            'form': Form(self._request), 'storage': storage, 'path': path,
            'filename': filename, 'mime_type': get_mime_type(fullname),
            'MIME_TYPES': MIME_TYPES, 'log': log, 'age': age,
            'has_lexer': self._has_lexer(fullname), 'content': content,
            'page_sizes': Paging.page_sizes}

    # -------------------------------------------------------------------------
    @view_config(route_name='file_download', permission='stg.read')
    def download(self):
        """Download a file."""
        storage = current_storage(self._request)[0]
        path = self._request.matchdict['path']
        real_path = join(self._request.registry.settings['storage.root'],
                         storage['storage_id'], *path[0:-1])
        if not isdir(real_path):
            raise HTTPNotFound(comment=_('This file does not exist!'))
        return file_download(self._request, real_path, (path[-1],))

    # -------------------------------------------------------------------------
    @view_config(route_name='file_revision', permission='stg.read')
    def revision(self):
        """Retrieve a revision of a file."""
        handler, filename, fullname, revision = self._file_info()
        content = handler.vcs.revision(fullname, revision)

        if content is None:
            self._request.session.flash(
                _('Unable to retrieve this revision: it was probably moved.'),
                'alert')
            return HTTPFound(self._request.route_path(
                'file_info', storage_id=handler.uid,
                path='/'.join(self._request.matchdict['path'])))

        download_name = u'%s.r%s%s' % (
            splitext(filename)[0], revision, splitext(filename)[1])
        response = Response(content, content_type=get_mime_type(fullname)[0])
        response.headerlist.append((
            'Content-Disposition',
            'attachment; filename="%s"' % download_name.encode('utf8')))
        return response

    # -------------------------------------------------------------------------
    @view_config(route_name='file_diff', permission='stg.read')
    def diff(self):
        """Differences between a version and current version."""
        handler, filename, fullname, revision = self._file_info()
        content = handler.vcs.diff(fullname, revision)

        download_name = u'%s.r%s.diff' % (splitext(filename)[0], revision)
        response = Response(content, content_type='text/x-diff')
        response.headerlist.append((
            'Content-Disposition',
            'attachment; filename="%s"' % download_name.encode('utf8')))
        return response

    # -------------------------------------------------------------------------
    def _file_info(self):
        """Return handler, filename, fullname, and revision."""
        handler = current_storage(self._request)[1]

        # pylint: disable = locally-disabled, W0142
        path = self._request.matchdict['path']
        revision = self._request.matchdict['revision']
        fullname = handler.vcs.full_path(*path)
        if fullname is None or isdir(fullname):
            raise HTTPForbidden()

        return handler, path[-1], fullname, revision

    # -------------------------------------------------------------------------
    def _display_form(self):
        """Return form for display view.

        :return: (:class:`~..lib.form.Form` instance)
        """
        schema = SchemaNode(Mapping())
        if 'seed' in self._request.params:
            schema.add(SchemaNode(String(), name='seed'))
        if 'name' in self._request.params:
            schema.add(SchemaNode(
                String(), name='name', validator=Length(max=PATH_LEN)))
        if 'message' in self._request.params:
            schema.add(SchemaNode(
                String(), name='vcs_user',
                validator=Length(max=ID_LEN), missing=None))
            schema.add(SchemaNode(String(), name='vcs_password', missing=None))
            schema.add(SchemaNode(
                String(), name='message',
                validator=Length(max=DESCRIPTION_LEN)))
        form = Form(self._request, schema=schema)
        return form

    # -------------------------------------------------------------------------
    def _display_action(self, form, storage, handler, path, filename):
        """Return form and current action for display view.

        :param form: (:class:`~..lib.form.Form` instance)
            Current form.
        :param storage: (dictionary)
            Storage dictionary.
        :param handler: (:class:`~..lib.handler.Handler` instance)
            Storage Control System.
        :param path: (string)
            Relative path to the current file.
        :param filename: (string)
            Name of the current file.
        :return: (tuple)
            A tuple such as ``(action, items, working)``.
        """
        working = False
        action, items = get_action(self._request)
        save_vcs_user(self._request, storage)
        if action == 'upl!' and 'vcs_change' not in self._request.params:
            if storage['perm'] != 'writer':
                raise HTTPForbidden(
                    comment=_("You can't modify this storage!"))
            if not form.validate():
                action = '%s?' % action[0:3]
                return action, items, working
            upload_file = self._request.params.get('upload_file')
            if upload_file.filename != filename:
                self._request.session.flash(
                    _('File names are different.'), 'alert')
                action = '%s?' % action[0:3]
                return action, items, working
            if not isinstance(upload_file, basestring):
                handler = self._request.registry['handler'].get_handler(
                    storage['storage_id'])
                working = handler.launch(
                    self._request, handler.upload,
                    (vcs_user(self._request, storage), path, upload_file,
                     filename, form.values.get('message', '-')))
        elif action == 'cls!' and 'container' in self._request.session:
            del self._request.session['container']
        elif action[0:4] in ('pck!', 'prc!'):
            add2container(
                self._request, action[0:3], action[4:7],
                join(storage['storage_id'], path), (filename,))
        elif action[0:4] == 'npk!' and 'project' in self._request.session \
                and self._request.session['project']['perm'] \
                in ('leader', 'packmaker'):
            items = create_pack(
                self._request, (filename,), join(storage['storage_id'], path))
        elif action == 'dup!':
            if not form.validate():
                action = '%s?' % action[0:3]
                return action, items, working
            items = (form.values['name'],)
            if splitext(items[0])[1] != splitext(filename)[1]:
                items = ('%s%s' % (items[0], splitext(filename)[1]),)
            working = handler.launch(
                self._request, handler.duplicate,
                (vcs_user(self._request, storage), path, filename, items[0],
                 form.values.get('message',
                                 get_localizer(self._request).translate(
                                     _('Duplication')))))

        return action, items, working

    # -------------------------------------------------------------------------
    def _file_opener(self, storage):
        """Return path, filename, fullname, opener and content."""
        # pylint: disable = locally-disabled, star-args
        path = self._request.matchdict['path']
        filename = path and path[-1] or ''
        fullname = join(self._request.registry.settings['storage.root'],
                        storage['storage_id'], *path)
        path = '/'.join(path)
        if not exists(fullname):
            raise HTTPNotFound(comment=_('This file does not exist!'))
        if isdir(fullname):
            return path, filename, None, None, None
        opener, content = \
            self._request.registry['opener'].get_opener(fullname, storage)
        return path, filename, fullname, opener, content

    # -------------------------------------------------------------------------
    def _search_results(self, storage, path):
        """Results of search

        :param storage: (dictionary)
            Storage dictionary.
        :param path: (string)
            Relative path to the current file.
        :return: (tuple or ``None``)
            A tuple such as ``(index, max)``
        """
        searches = 'search' in self._request.session \
            and self._request.session['search'].get('r') \
            and [(k[2], k[3]) for k in self._request.session['search']['r']]
        searches = searches and (storage['storage_id'], path) in searches and (
            searches.index((storage['storage_id'], path)) + 1, len(searches))
        return searches

    # -------------------------------------------------------------------------
    def _search_indexes(self):
        """Store search indexes in session and return fields and values for
        queries. ``self._request.session['search']['i']`` is a dictionary such
        as ``{index_id: (label, type, options),...}``.

        :return: (tuple)
            A tuple like ``(fields, values)``.
        """
        # Retrieve indexers
        if 'search' in self._request.session:
            indexes = self._request.session['search']['i']
        else:
            indexes = {}
            lang = self._request.session['lang']
            default_lang = self._request.registry.settings[
                'pyramid.default_locale_name']
            for indexer in DBSession.query(Indexer):
                if indexer.indexer_id == 'extract':
                    continue
                values = indexer.value_type == 'select' \
                    and [(k.value, k.label) for k in indexer.values] or None
                indexes[indexer.indexer_id] = (
                    indexer.label(lang, default_lang), indexer.value_type,
                    values and sorted(values, key=lambda k: k[1]) or None)
            self._request.session['search'] = {
                'i': indexes, 's': [], 'l': 20, 'r': None,
                'q': [None, '', 'AND', None, '', 'AND', None, '']}

        # Compute values
        values = []
        for k in range(3):
            index = self._request.params.get('q%dindex' % k) \
                or self._request.session['search']['q'][3 * k]
            values.append(
                index and index in indexes and indexes[index][2] or None)

        # Fields
        return \
            sorted([(k, indexes[k][0]) for k in indexes], key=lambda k: k[1]),\
            values

    # -------------------------------------------------------------------------
    def _search_scope(self):
        """Find  eligible storage IDs and compute scope.

        :return: (tuple)
            A tuple such as ``(scope, storages_ids)``.
            Scope of search.
        """
        session = self._request.session
        route = self._request.route_path('storage_root', storage_id='')
        indexed_storages = [
            k[0] for k in DBSession.query(Storage.storage_id).filter(
                Storage.indexed_files != NULL)]

        scope = []
        storage_ids = []
        for item in session.get('menu', ''):
            for subitem in item[3] or ():
                if subitem[1] and subitem[1].startswith(route):
                    storage_id = subitem[1][len(route):]
                    if storage_id in indexed_storages:
                        scope.append((storage_id, subitem[0]))
                        storage_ids.append(storage_id)
                        self._request.registry['handler'].get_handler(
                            storage_id)

        if 'storage' in session and session['storage']['indexed'] \
                and session['storage']['storage_id'] not in storage_ids:
            scope.insert(
                0, (session['storage']['storage_id'],
                    session['storage']['label']))
            storage_ids.append(session['storage']['storage_id'])
            self._request.registry['handler'].get_handler(
                session['storage']['storage_id'])

        return scope, storage_ids

    # -------------------------------------------------------------------------
    def _search_form(self, storage_ids):
        """Return a search form.

        :param storage_ids: (list)
            Available storage IDs.
        :return: (:class:`~.lib.form.Form` instance)
        """
        # Schema
        index_ids = self._request.session['search']['i'].keys()
        schema = SchemaNode(Mapping())
        schema.add(SchemaNode(
            String(), name='q0index',
            validator=OneOf(index_ids + ['filename', '*'])))
        schema.add(SchemaNode(
            String(), name='q1index', validator=OneOf(index_ids),
            missing=None))
        schema.add(SchemaNode(
            String(), name='q2index', validator=OneOf(index_ids),
            missing=None))
        schema.add(SchemaNode(String(), name='q0value'))
        schema.add(SchemaNode(String(), name='q1value', missing=None))
        schema.add(SchemaNode(String(), name='q2value', missing=None))
        schema.add(SchemaNode(
            String(), name='q1op', validator=OneOf(('AND', 'OR', 'NOT')),
            missing='AND'))
        schema.add(SchemaNode(
            String(), name='q2op', validator=OneOf(('AND', 'OR', 'NOT')),
            missing='AND'))
        for sid in storage_ids:
            schema.add(SchemaNode(Boolean(), name='~%s' % sid, missing=False))
        schema.add(SchemaNode(Boolean(), name='~ALL~', missing=False))
        schema.add(SchemaNode(Integer(), name='limit'))

        # Defaults
        defaults = {'limit': 20}
        if self._request.session['search']['q'][0]:
            defaults['q0index'] = self._request.session['search']['q'][0]
            defaults['q0value'] = self._request.session['search']['q'][1]
            defaults['q1op'] = self._request.session['search']['q'][2]
            defaults['q1index'] = self._request.session['search']['q'][3]
            defaults['q1value'] = self._request.session['search']['q'][4]
            defaults['q2op'] = self._request.session['search']['q'][5]
            defaults['q2index'] = self._request.session['search']['q'][6]
            defaults['q2value'] = self._request.session['search']['q'][7]
            defaults['limit'] = self._request.session['search']['l']
        if self._request.session['search']['s']:
            for storage_id in self._request.session['search']['s']:
                defaults['~%s' % storage_id] = True
        elif 'storage' in self._request.session:
            defaults = {
                '~%s' % self._request.session['storage']['storage_id']: True,
                'limit': 20}

        form = Form(self._request, schema=schema, defaults=defaults)
        if not self._request.params.get('q1index') \
                and not defaults.get('q1index'):
            form.static('q1value')
            form.values['q1value'] = ''
        if not self._request.params.get('q2index') \
                and not defaults.get('q2index'):
            form.static('q2value')
            form.values['q2value'] = ''
        return form

    # -------------------------------------------------------------------------
    def _search_query(self, fields, values):
        """Search files in storages and return a result.

        :param values: (list)
            List of available fields.
        :param values: (dictionary)
            Search form values.
        :return: (list)
            A list of tuples such as ``(score, file_type, storage_id,
            path)``.

        This method stores query in ``session['search']['q']``, scope in
        ``session['search']['s']`` and results in ``session['search']['r']``.
        """
        # Register query
        values['q1index'] = values['q1value'] and values['q1index'] or None
        values['q2index'] = values['q2value'] and values['q2index'] or None
        self._request.session['search']['q'] = (
            values['q0index'], values['q0value'],
            values['q1op'], values['q1index'], values['q1value'],
            values['q2op'], values['q2index'], values['q2value'])
        self._request.session['search']['l'] = values['limit']

        # Compute scope
        scope = []
        for storage_id in values:
            if storage_id[0] == '~' and values[storage_id]:
                scope.append(storage_id[1:])
                if storage_id == '~ALL~':
                    scope = ['ALL~']
                    break
        if not scope:
            self._request.session.flash(_('Select a storage!'), 'alert')
            return
        self._request.session['search']['s'] = scope
        if scope[0] == 'ALL~':
            scope = [k[0] for k in query_storages(
                DBSession.query(Storage.storage_id),
                self._request.session['user_id'], True)]

        # Compute query
        fieldnames = set((
            values['q0index'], values['q1index'], values['q2index'])) \
            - set((None,))
        fieldnames = '*' in fieldnames and dict(fields).keys() + ['filename'] \
            or tuple(fieldnames)
        if not values['q1index']:
            query = values['q0value']
        elif not values['q2index']:
            query = '%s:(%s) %s %s:(%s)' \
                % self._request.session['search']['q'][0:5]
        else:
            query = '(%s:(%s) %s %s:(%s)) %s %s:(%s)' \
                % self._request.session['search']['q']

        # Process query in scope
        results = []
        for storage_id in scope:
            results += self._request.registry['handler'].search(
                storage_id, fieldnames, query, values['limit'] + 1)

        # Cleanup and complete result
        results = sorted(results, key=lambda item: item[0], reverse=True)
        results = results[0:values['limit'] + 1]
        root = self._request.registry.settings['storage.root']
        for result in results:
            result[1] = get_mime_type(join(root, result[2], result[3]))[1]
        self._request.session['search']['r'] = results
        return results

    # -------------------------------------------------------------------------
    def _pop_read_write_routes(self, storage):
        """Remove from the bread crumbs.
        :param storage: (dictionary)
            Storage dictionary.
        """
        path = self._request.breadcrumbs.current_path()
        if path.startswith(self._request.route_path(
                'file_read', storage_id=storage['storage_id'], path='')) \
            or path.startswith(self._request.route_path(
                'file_render', storage_id=storage['storage_id'], path='')) \
            or path.startswith(self._request.route_path(
                'file_write', storage_id=storage['storage_id'], path='')) \
            or path.startswith(self._request.route_path(
                'file_edit', storage_id=storage['storage_id'], path='')):
            self._request.breadcrumbs.pop()

    # -------------------------------------------------------------------------
    @classmethod
    def _has_lexer(cls, fullname):
        """Return ``True`` if a lexer exists.

        :param fullname: (string)
            Full path to the file to display.
        :return: (boolean)
        """
        if fullname[-4:] in ('.rnc', '.rng'):
            return True
        try:
            get_lexer_for_filename(fullname)
        except ClassNotFound:
            return False
        return True

    # -------------------------------------------------------------------------
    @classmethod
    def _highlight(cls, fullname, content):
        """Return a literal XHTML with syntax highlighting of the content.

        :param fullname: (string)
            Full path to the file to display.
        :param content: (string)
            Text to highlight.
        """
        try:
            content = content.decode('utf8')
        except UnicodeDecodeError:
            pass

        if fullname[-4:] == '.rnc':
            return literal('<div><pre>%s</pre></div>') % content
        elif fullname[-4:] == '.rng':
            return literal(highlight(content, XmlLexer(), HtmlFormatter()))
        return literal(highlight(
            content, get_lexer_for_filename(fullname), HtmlFormatter()))
