# $Id: storage.py 828a3c221ecf 2014/12/09 15:00:26 Patrick $
# pylint: disable = locally-disabled, C0322
"""Storage view callables."""

from os.path import join, isdir, dirname
from webhelpers2.html import HTML
from sqlalchemy import select, desc
from colander import Mapping, SchemaNode, String, Integer
from colander import All, Length, Regex, OneOf

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPForbidden
from pyramid.i18n import get_localizer

from ..lib.utils import _, MIME_TYPES, has_permission, age
from ..lib.utils import normalize_spaces, settings_get_list
from ..lib.xml import upload_configuration, export_configuration
from ..lib.viewutils import vcs_user, save_vcs_user, paging_users
from ..lib.viewutils import paging_groups, get_action, file_download
from ..lib.viewutils import add2container, query_storages, current_storage
from ..lib.packutils import create_pack
from ..lib.form import Form
from ..lib.widget import TabSet, sortable_column, Paging
from ..models import NULL, ID_LEN, LABEL_LEN, DESCRIPTION_LEN, PATH_LEN
from ..models import DBSession, close_dbsession
from ..models.users import User
from ..models.groups import GROUPS_USERS, Group
from ..models.storages import STORAGE_ACCESS, VCS_ENGINES, STORAGE_PERMS
from ..models.storages import Storage, StorageOpener, StorageUser, StorageGroup


STORAGE_SETTINGS_TABS = (
    _('Description'), _('Openers'), _('Authorized members'),
    _('Authorized groups'))
REFRESH = {
    900: _('every 15 minutes'), 1800: _('every 30 minutes'),
    3600: _('every hour'), 7200: _('every 2 hours'),
    14400: _('every 4 hours'), 28800: _('every 8 hours'),
    86400: _('every day')}
INDEXED = {
    r'\.(txt|ini|rst|xml)$': _('Texts'),
    r'\.(txt|ini|rst|xml|png|jpg|jpeg|tif|tiff|gif|svg)$': _('Texts, images'),
    r'\.xml$': _('XML files'),
    r'\.(xml|png)$': _('XML files, PNG images'),
    r'\.(xml|png|jpg|jpeg|tif|tiff|gif|svg)$': _('XML files, images'),
    r'\.(png|jpg|jpeg|tif|tiff|gif|svg)$': _('Images'),
    r'\.(wav|ogg)$': _('Audios'),
    r'\.(mp4|avi)$': _('Videos'),
    r'\.(png|jpg|jpeg|tif|tiff|gif|svg|wav|ogg|mpg|mp4|avi)$':
        _('Images, audios, videos'),
    r'\.(txt|ini|rst|xml|png|jpg|jpeg|tif|tiff|gif|svg|wav|ogg|mpg|mp4|avi)$':
        _('Texts, images, audios, videos')}


# =============================================================================
class StorageView(object):
    """Class to manage storages."""

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        request.add_finished_callback(close_dbsession)
        self._request = request
        self._vcs_engines = dict([
            (k, VCS_ENGINES[k]) for k
            in settings_get_list(request.registry.settings, 'storage.vcs')])

    # -------------------------------------------------------------------------
    @view_config(
        route_name='storage_admin', renderer='../Templates/stg_admin.pt',
        permission='stg.update')
    def admin(self):
        """List storages for administration purpose."""
        action, items = get_action(self._request)
        if action == 'imp!':
            upload_configuration(self._request, 'stg_manager', 'storage')
            action = ''
            del self._request.session['menu']
        elif action[0:4] == 'del!':
            if not has_permission(self._request, 'stg_manager'):
                raise HTTPForbidden()
            storage_root = self._request.registry.settings['storage.root']
            for storage_id in items:
                Storage.delete(storage_root, storage_id)
                self._request.registry['handler'].remove_handler(storage_id)
            action = ''
            self._request.registry['handler'].delete_index()
            del self._request.session['menu']
        elif action[0:4] == 'exp!':
            return self._export_storages(items)

        paging, defaults = self._paging_storages()
        form = Form(self._request, defaults=defaults)
        groups = [(k.group_id, k.label) for k in
                  DBSession.query(Group).join(StorageGroup)]

        depth = (self._request.breadcrumbs.current_path() ==
                 self._request.route_path('site_admin') and 3) or 2
        self._request.breadcrumbs.add(_('Storage administration'), depth)
        return {
            'form': form, 'paging': paging, 'action': action,
            'groups': groups, 'STORAGE_ACCESS': STORAGE_ACCESS,
            'vcs_engines': self._vcs_engines,
            'i_editor': has_permission(self._request, 'stg_editor'),
            'i_manager': has_permission(self._request, 'stg_manager')}

    # -------------------------------------------------------------------------
    @view_config(
        route_name='storage_index', renderer='../Templates/stg_index.pt',
        permission='stg.read')
    @view_config(route_name='storage_index', renderer='json', xhr=True)
    def index(self):
        """List authorized storages."""
        # Action
        user_id = self._request.session['user_id']
        action, items = get_action(self._request)
        if action[0:4] == 'exp!':
            return self._export_storages(items)
        elif action[0:3] == 'men':
            stg_user = DBSession.query(StorageUser).filter_by(
                storage_id=action[4:], user_id=user_id).first()
            if stg_user is None:
                stg_user = StorageUser(action[4:], user_id)
                DBSession.add(stg_user)
            stg_user.in_menu = action[3] == '+'
            DBSession.commit()
            del self._request.session['menu']
        elif action == 'cls!' and 'container' in self._request.session:
            del self._request.session['container']

        # Environment
        paging, defaults = self._paging_storages(user_id)
        refresh = int(self._request.registry.settings.get('refresh.long', 5))

        # Ajax
        if self._request.is_xhr:
            action, prgrss = self._request.registry['handler'].progress(
                [k.storage_id for k in paging])
            return {
                'working': action, 'refresh': refresh,
                'status': dict([(k, prgrss[k][0]) for k in prgrss])}

        # Changes
        changes = {}
        for storage in paging:
            handler = self._request.registry['handler']\
                .get_handler(storage.storage_id, storage)
            changes[handler.uid] = list(handler.vcs.last_change())
            changes[handler.uid][0] = (
                age(changes[handler.uid][0]),
                changes[handler.uid][0].isoformat(' ').partition('.')[0])
            force = (action == 'syn!%s' % storage.storage_id) or \
                    (action == 'syn!#' and storage.storage_id in items)
            if handler.synchronize(self._request, force):
                handler.cache.clear()
        in_menus = [k[0] for k in DBSession.query(StorageUser.storage_id)
                    .filter_by(user_id=self._request.session['user_id'])
                    .filter_by(in_menu=True).all()]

        # Work in progress
        action, prgrss = \
            self._request.registry['handler'].progress(changes.keys())
        if action and 'ajax' not in self._request.params:
            self._request.response.headerlist.append(('Refresh', str(refresh)))

        self._request.breadcrumbs.add(
            _('All storages'),
            'container' in self._request.session and 10 or 2)
        return {
            'vcs_engines': self._vcs_engines, 'paging': paging,
            'form': Form(self._request, defaults=defaults),
            'changes': changes, 'in_menus': in_menus, 'progress': prgrss,
            'working': action, 'refresh': refresh}

    # -------------------------------------------------------------------------
    @view_config(route_name='storage_view',
                 renderer='../Templates/stg_view.pt',
                 permission='stg.read')
    def view(self):
        """Show storage settings with its users and groups."""
        # Environment
        storage = current_storage(self._request, only_dict=False)[0]
        tab_set = TabSet(self._request, STORAGE_SETTINGS_TABS)
        members = DBSession.query(
            User.user_id, User.login, User.name, StorageUser.perm)\
            .join(StorageUser)\
            .filter(StorageUser.storage_id == storage.storage_id)\
            .filter(StorageUser.perm != NULL).order_by(User.name)
        member_groups = DBSession.query(
            Group.group_id, Group.label, StorageGroup.perm)\
            .filter(StorageGroup.storage_id == storage.storage_id)\
            .filter(Group.group_id == StorageGroup.group_id)\
            .order_by(Group.label).all()
        i_editor = has_permission(self._request, 'stg_editor') \
            or self._request.session['storage']['perm'] == 'editor'
        openers = [
            k.opener_id for k in sorted(storage.openers, key=lambda k: k.sort)]
        openers = self._request.registry['opener'].descriptions(
            self._request, openers)
        indexed = INDEXED.get(storage.indexed_files, storage.indexed_files)

        # Action
        action = get_action(self._request)[0]
        if action == 'exp!':
            return self._export_storages((
                self._request.matchdict.get('storage_id'),))
        elif action == 'rec!':
            self._vcs_recover(storage)

        # Breadcrumbs
        self._request.breadcrumbs.add(
            _('Storage settings'), replace=self._request.route_path(
                'storage_edit', storage_id=storage.storage_id))
        return {
            'form': Form(self._request), 'tab_set': tab_set,
            'STORAGE_ACCESS': STORAGE_ACCESS, 'REFRESH': REFRESH,
            'PERMS': STORAGE_PERMS, 'PROJECT_ENTRIES': None,
            'vcs_engines': self._vcs_engines, 'storage': storage,
            'indexed': indexed, 'openers': openers, 'members': members,
            'member_groups': member_groups, 'i_editor': i_editor}

    # -------------------------------------------------------------------------
    @view_config(
        route_name='storage_create', renderer='../Templates/stg_edit.pt',
        permission='stg.create')
    def create(self):
        """Create a storage."""
        form, tab_set = self._settings_form()

        if form.validate():
            storage = self._create(form.values)
            if storage is not None:
                self._request.breadcrumbs.pop()
                return HTTPFound(self._request.route_path(
                    'storage_edit', storage_id=storage.storage_id))
        if form.has_error():
            self._request.session.flash(_('Correct errors.'), 'alert')

        self._request.breadcrumbs.add(_('Storage creation'))
        return {
            'form': form, 'tab_set': tab_set,
            'STORAGE_ACCESS': STORAGE_ACCESS, 'REFRESH': REFRESH,
            'PERMS': STORAGE_PERMS, 'vcs_engines': self._vcs_engines,
            'INDEXED': INDEXED, 'storage': None, 'allopeners': None,
            'members': None, 'group_members': None, 'paging': None,
            'groups': None}

    # -------------------------------------------------------------------------
    @view_config(
        route_name='storage_edit', renderer='../Templates/stg_edit.pt')
    def edit(self):
        """Edit storage settings."""
        # Authorization
        storage = current_storage(self._request, only_dict=False)[0]
        if not has_permission(self._request, 'stg_editor') \
                and self._request.session['storage']['perm'] != 'editor':
            raise HTTPForbidden()

        # Action
        action, allopeners, paging, groups = self._edit_action(storage)

        # Environment
        form, tab_set = self._settings_form(storage)
        members = DBSession.query(
            User.user_id, User.login, User.name, StorageUser.perm)\
            .filter(StorageUser.storage_id == storage.storage_id)\
            .filter(User.user_id == StorageUser.user_id)\
            .order_by(User.name).all()
        member_groups = DBSession.query(
            Group.group_id, Group.label, StorageGroup.perm)\
            .filter(StorageGroup.storage_id == storage.storage_id)\
            .filter(Group.group_id == StorageGroup.group_id)\
            .order_by(Group.label).all()
        openers = [
            k.opener_id for k in sorted(storage.openers, key=lambda k: k.sort)]
        openers = self._request.registry['opener'].descriptions(
            self._request, openers)

        # Save
        view_path = self._request.route_path(
            'storage_view', storage_id=storage.storage_id)
        if action == 'sav!' and form.validate(storage):
            storage.set_vcs_password(
                self._request.registry.settings, form.values.get('password'))
            for user in storage.users:
                user.perm = form.values['usr_%d' % user.user_id]
            for group in storage.groups:
                group.perm = form.values['grp_%s' % group.group_id]
            DBSession.commit()
            self._request.registry['handler'].remove_handler(
                storage.storage_id)
            self._request.registry['handler'].delete_index()
            del self._request.session['menu']
            return HTTPFound(view_path)
        if form.has_error():
            self._request.session.flash(_('Correct errors.'), 'alert')

        # Breadcrumbs
        self._request.breadcrumbs.add(
            _('Storage settings'), replace=view_path)

        return {
            'form': form, 'action': action, 'tab_set': tab_set,
            'STORAGE_ACCESS': STORAGE_ACCESS, 'REFRESH': REFRESH,
            'PERMS': STORAGE_PERMS, 'PROJECT_ENTRIES': None,
            'vcs_engines': self._vcs_engines, 'storage': storage,
            'INDEXED': INDEXED, 'openers': openers, 'allopeners': allopeners,
            'members': members, 'member_groups': member_groups,
            'paging': paging, 'groups': groups}

    # -------------------------------------------------------------------------
    @view_config(
        route_name='storage_root', renderer='../Templates/stg_browse.pt',
        permission='stg.read')
    @view_config(
        route_name='storage_browse', renderer='../Templates/stg_browse.pt',
        permission='stg.read')
    def browse(self):
        """Browse a storage."""
        # Environment
        storage, handler = current_storage(self._request)
        storage_id = storage['storage_id']
        path = self._request.matchdict.get('path', [])
        path, real_path, html_path = self._html_path(storage_id, path)
        refresh = self._request.registry.settings.get('refresh.short', '2')

        # Form, action & working status
        form, action, items, working = \
            self._browse_action(storage, handler, path)
        if action[0:4] == 'dnl!':
            return file_download(self._request, real_path, items)
        elif action[0:4] == 'sch!':
            return HTTPFound(self._request.route_path('file_search'))
        elif action[0:4] == 'npk!' and items[0] is not None:
            return HTTPFound(self._request.route_path(
                'pack_edit', project_id=items[0], pack_id=items[1],
                _anchor='tab0'))

        # Work in progress
        working, progress = self._request\
            .registry['handler'].progress((storage_id,), working)
        if working:
            self._request.response.headerlist.append(('Refresh', refresh))
        if storage_id in progress and progress[storage_id][0] == 'error':
            self._request.session.flash(progress[storage_id][1], 'alert')

        # Directory content
        dirs, files = handler.dir_infos(
            path, self._request.params.get('sort', '+name'), working)
        if working:
            handler.cache.clear()

        self._request.breadcrumbs.add(_('Storage browsing'), root_chunks=3)
        return {
            'form': form, 'action': action, 'working': working,
            'sortable_column': sortable_column, 'storage': storage,
            'path': path, 'html_path': html_path, 'dirs': dirs,
            'files': files, 'MIME_TYPES': MIME_TYPES,
            'vcs_engines': self._vcs_engines}

    # -------------------------------------------------------------------------
    def _paging_storages(self, user_id=None):
        """Return a :class:`~..lib.widget.Paging` object filled
        with storages.

        :param user_id: (integer, optional)
            Select only storages of user ``user_id``.
        :return: (tuple)
            A tuple such as ``(paging, filters)`` where ``paging`` is a
            :class:`~..lib.widget.Paging` object and ``filters`` a
            dictionary  of filters.
        """
        # Parameters
        paging_id = user_id is None and 'storages!' or 'storages'
        params = Paging.params(self._request, paging_id, '+label')
        if user_id is not None and 'f_access' in params:
            del params['f_access']

        # Query
        query = DBSession.query(Storage)
        if user_id is not None:
            query = query_storages(query, user_id)
        elif 'f_login' in params:
            query = query.join(StorageUser).join(User)\
                .filter(User.login == params['f_login'])\
                .filter(StorageUser.perm != NULL)
        if 'f_id' in params:
            query = query.filter(Storage.storage_id.ilike(
                '%%%s%%' % params['f_id']))
        if 'f_group' in params:
            query = query.join(StorageGroup).filter(
                StorageGroup.group_id == params['f_group'])
        if 'f_label' in params:
            query = query.filter(
                Storage.label.ilike('%%%s%%' % params['f_label']))
        if 'f_access' in params and params['f_access'] != '*':
            query = query.filter(Storage.access == params['f_access'])
        elif 'f_access' not in params:
            query = query.filter(Storage.access != 'closed')
        if 'f_engine' in params:
            query = query.filter(Storage.vcs_engine == params['f_engine'])

        # Order by
        oby = 'storages.%s' % params['sort'][1:]
        query = query.order_by(desc(oby) if params['sort'][0] == '-' else oby)

        return Paging(self._request, paging_id, query), params

    # -------------------------------------------------------------------------
    def _export_storages(self, storage_ids):
        """Export storages.

        :param storage_ids: (list)
            List of storage IDs to export.
        :return: (:class:`pyramid.response.Response` instance)
        """
        i_editor = has_permission(self._request, 'stg_editor')
        user_id = self._request.session['user_id']
        groups = set([k.group_id for k in DBSession.execute(
            select([GROUPS_USERS], GROUPS_USERS.c.user_id == user_id))])
        elements = []
        for storage in DBSession.query(Storage)\
                .filter(Storage.storage_id.in_(storage_ids))\
                .order_by('label'):
            if i_editor or storage.access == 'open' or \
               user_id in [k.user_id for k in storage.users] or \
               (groups and groups & set([k.group_id for k in storage.groups])):
                elements.append(storage.xml())

        name = '%s_storages.pfstg' % self._request.registry.settings.get(
            'skin.label', 'publiforge')
        return export_configuration(elements, name)

    # -------------------------------------------------------------------------
    def _settings_form(self, storage=None):
        """Return a storage settings form.

        :param storage: (:class:`~..models.storages.Storage` instance,
            optional) Current storage object.
        :return: (tuple)
            A tuple such as ``(form, tab_set)``.
        """
        vcs_engine = storage and storage.vcs_engine \
            or self._request.params.get('vcs_engine')

        # Schema
        schema = SchemaNode(Mapping())
        schema.add(SchemaNode(
            String(), name='access', validator=OneOf(STORAGE_ACCESS.keys())))
        if storage is None:
            schema.add(SchemaNode(
                String(), name='storage_id',
                validator=All(Regex(r'^[\w_][\w_.-]+$'), Length(max=ID_LEN))))
        schema.add(SchemaNode(
            String(), name='label', validator=Length(min=2, max=LABEL_LEN)))
        schema.add(SchemaNode(
            String(), name='description',
            validator=Length(max=DESCRIPTION_LEN), missing=''))
        if storage is None:
            schema.add(SchemaNode(
                String(), name='vcs_engine',
                validator=OneOf(self._vcs_engines.keys())))
        if vcs_engine is None or vcs_engine not in ('none', 'local'):
            schema.add(SchemaNode(
                String(), name='vcs_url', validator=Length(max=PATH_LEN)))
            schema.add(SchemaNode(
                String(), name='vcs_user', validator=Length(max=ID_LEN),
                missing=None))
            schema.add(SchemaNode(String(), name='password', missing=None))
        if vcs_engine is None or vcs_engine in ('none', 'local'):
            schema.add(SchemaNode(
                String(), name='public_url',
                validator=Length(max=PATH_LEN), missing=None))
        schema.add(SchemaNode(Integer(), name='refresh', missing=3600))
        schema.add(SchemaNode(String(), name='indexed_files', missing=None))
        if storage is not None:
            for user in storage.users:
                schema.add(SchemaNode(
                    String(), name='usr_%d' % user.user_id,
                    validator=OneOf(STORAGE_PERMS.keys())))
            for group in storage.groups:
                schema.add(SchemaNode(
                    String(), name='grp_%s' % group.group_id,
                    validator=OneOf(STORAGE_PERMS.keys())))

        defaults = {'access': 'open', 'vcs_engine': 'local', 'refresh': 3600}
        if 'paging' in self._request.session:
            if 'groups' in self._request.session['paging'][1]:
                defaults.update(self._request.session['paging'][1]['groups'])
            if 'users' in self._request.session['paging'][1]:
                defaults.update(self._request.session['paging'][1]['users'])

        return (
            Form(self._request, schema=schema, defaults=defaults, obj=storage),
            TabSet(self._request, STORAGE_SETTINGS_TABS))

    # -------------------------------------------------------------------------
    def _create(self, values):
        """Create a storage.

        :param values: (dictionary)
            Form values.
        :return: (:class:`~..models.storages.Storage` instance or ``None``)
        """
        # Check existence
        storage_id = values['storage_id'].strip()
        storage = DBSession.query(Storage).filter_by(
            storage_id=storage_id).first()
        if storage is None:
            label = normalize_spaces(values['label'], LABEL_LEN)
            storage = DBSession.query(Storage).filter_by(
                label=label).first()
        if storage is not None:
            self._request.session.flash(
                _('This storage already exists.'), 'alert')
            return

        # Create storage
        # pylint: disable = locally-disabled, W0142
        record = dict(
            [(k, values[k]) for k in values if hasattr(Storage, k)])
        storage = Storage(self._request.registry.settings, **record)
        storage.set_vcs_password(
            self._request.registry.settings, values.get('password'))
        DBSession.add(storage)
        DBSession.commit()

        # Clone
        handler = self._request.registry['handler'].get_handler(
            storage.storage_id, storage)
        handler.clone(self._request)

        return storage

    # -------------------------------------------------------------------------
    @classmethod
    def _save(cls, storage, values):
        """Save a storage settings.

        :param storage: (:class:`~..models.storages.Storage` instance)
            Storage to update.
        :param values: (dictionary)
            Form values.
        :return: (boolean)
            ``True`` if succeeds.
        """
        # Update permissions
        for user in storage.users:
            user.perm = values['perm_%d' % user.user_id]

        DBSession.commit()
        return True

    # -------------------------------------------------------------------------
    def _edit_action(self, storage):
        """
        :param storage: (:class:`~..models.storages.Storage` instance)
            Storage object.
        :return: (tuple)
            A tuple such as ``(action, allopeners, paging, groups)``.
        """
        paging = groups = allopeners = None
        action, items = get_action(self._request)
        if action == 'aop?':
            allopeners = self._request.registry['opener'].descriptions(
                self._request)
        elif action[0:4] == 'aop!':
            self._add_openers(storage, items)
        elif action[0:3] in ('mup', 'dwn'):
            self._swap_openers(action[0:3], action[4:], storage)
            DBSession.commit()
        elif action[0:4] == 'rop!':
            DBSession.query(StorageOpener).filter_by(
                storage_id=storage.storage_id, opener_id=action[4:]).delete()
            DBSession.commit()
            if 'storage' in self._request.session:
                del self._request.session['storage']
        elif action == 'aur?' or \
                (not action and self._request.GET.get('paging_id') == 'users'):
            groups = DBSession.query(Group.group_id, Group.label).all()
            paging = paging_users(self._request)[0]
        elif action[0:4] == 'aur!':
            self._add_members(storage, items)
        elif action[0:4] == 'rur!':
            DBSession.query(StorageUser).filter_by(
                storage_id=storage.storage_id, user_id=int(action[4:]))\
                .delete()
            DBSession.commit()
            del self._request.session['menu']
        elif action == 'agp?' or (
                not action and self._request.GET.get('paging_id') == 'groups'):
            paging = paging_groups(self._request)[0]
        elif action[0:4] == 'agp!':
            self._add_member_groups(storage, items)
        elif action[0:4] == 'rgp!':
            DBSession.query(StorageUser).filter_by(
                storage_id=storage.storage_id, perm=None).delete()
            DBSession.query(StorageGroup).filter_by(
                storage_id=storage.storage_id, group_id=action[4:]).delete()
            DBSession.commit()
            del self._request.session['menu']

        return action, allopeners, paging, groups

    # -------------------------------------------------------------------------
    def _add_openers(self, storage, new_ids):
        """Add selected openers to the storage.

        :param new_ids: (list):
            List of openers to add.
        :param storage: (:class:`~..models.storages.Storage` instance)
            Current storage object.
        """
        if not has_permission(self._request, 'stg_editor') \
                and self._request.session['storage']['perm'] != 'editor':
            return

        openers = [k for k in sorted(storage.openers, key=lambda k: k.sort)]
        opener_ids = [k.opener_id for k in openers]
        for opener_id in sorted(new_ids, reverse=True):
            if opener_id not in opener_ids:
                openers.insert(0, StorageOpener(storage.storage_id, opener_id))
                DBSession.add(openers[0])
        for num, opener in enumerate(openers):
            opener.sort = num + 1
        DBSession.commit()
        if 'storage' in self._request.session:
            del self._request.session['storage']

    # -------------------------------------------------------------------------
    def _add_members(self, storage, new_ids):
        """Add selected users to the storage.

        :param new_ids: (list):
            List of users to add.
        :param storage: (:class:`~..models.storages.Storage` instance)
            Current storage object.
        """
        if not has_permission(self._request, 'stg_editor') \
                and self._request.session['storage']['perm'] != 'editor':
            return

        user_ids = [k.user_id for k in storage.users]
        for user_id in new_ids:
            user_id = int(user_id)
            if user_id not in user_ids:
                storage.users.append(StorageUser(
                    storage.storage_id, user_id))
        DBSession.commit()
        del self._request.session['menu']

    # -------------------------------------------------------------------------
    def _add_member_groups(self, storage, new_ids):
        """Add selected groups to the storage.

        :param new_ids: (list):
            List of groups to add.
        :param storage_id: (:class:`~..models.storages.Storage` instance)
            Storage object.
        """
        if not has_permission(self._request, 'stg_editor') \
                and self._request.session['storage']['perm'] != 'editor':
            return

        group_ids = [k.group_id for k in storage.groups]
        for group_id in new_ids:
            if group_id not in group_ids:
                storage.groups.append(StorageGroup(
                    storage.storage_id, group_id))
        DBSession.commit()
        del self._request.session['menu']

    # -------------------------------------------------------------------------
    def _html_path(self, storage_id, path):
        """Return relative path in storage, real path and path in one string
        with ``<a>`` tags.

        :param storage_id: (string)
            Storage ID.
        :param path: (list)
            Splitted relative path inside the storage.
        :return: (tuple)
            A tuple such as ``(path, real_path, html_path)`` or a
            :class:`pyramid.httpexceptions.`HTTPNotFound` exception..
        """
        # Path exists?
        # pylint: disable = locally-disabled, star-args
        real_path = join(self._request.registry.settings['storage.root'],
                         storage_id, *path)
        if not isdir(real_path) and path:
            real_path = dirname(real_path)
            path = path[0:-1]
        if not isdir(real_path):
            raise HTTPNotFound(comment=_('This directory does not exist!'))

        # Root path
        if len(path) == 0:
            return '', real_path, HTML.span(storage_id)

        # Other path
        html = HTML.a(storage_id, href=self._request.route_path(
            'storage_root', storage_id=storage_id))
        for index in range(len(path) - 1):
            html += ' / ' + HTML.a(path[index], href=self._request.route_path(
                'storage_browse', storage_id=storage_id,
                path='/'.join(path[0:index + 1])).decode('utf8'))
        html += ' / ' + HTML.span(path[-1])

        return join('.', *path), real_path, html

    # -------------------------------------------------------------------------
    def _browse_action(self, storage, handler, path):
        """Return form, current action and working status for browse view.

        :param storage: (dictionary)
            Storage dictionary.
        :param handler: (:class:`~..lib.handler.Handler` instance)
            Storage Control System.
        :param path:
            Relative path in storage.
        :return: (tuple)
            A tuple such as ``(form, action, items, working)``.
        """
        working = False
        action, items = get_action(self._request)
        form = self._vcs_user_form(storage, action)

        # Check
        if action[0:4] in ('upl!', 'new!', 'dir!', 'ren!', 'del!'):
            if storage['perm'] != 'writer':
                raise HTTPForbidden(
                    comment=_("You can't modify this storage!"))
            if not form.validate():
                action = '%s?%s' % (action[0:3], action[4:])
                return form, action, items, working

        # Action
        if action[0:4] == 'upl!':
            upload_file = self._request.params.get('upload_file')
            if not isinstance(upload_file, basestring):
                working = handler.launch(
                    self._request, handler.upload,
                    (vcs_user(self._request, storage), path, upload_file,
                     items and items[0] or None,
                     form.values.get('message', '-')))
        elif action[0:4] == 'ren!':
            working = handler.launch(
                self._request, handler.rename,
                (vcs_user(self._request, storage), path, action[4:],
                 form.values['new_name'], form.values.get('message', '-')))
            action = ''
        elif action[0:4] == 'del!':
            working = handler.launch(
                self._request, handler.remove,
                (vcs_user(self._request, storage), path, items,
                 form.values.get('message', '-')))
        elif action == 'sch!' and 'search' in self._request.session:
            del self._request.session['search']
        elif action in ('new?', 'new!', 'dir!'):
            working |= self._browse_action_create(
                storage, handler, path, action, form)
        elif action[0:4] in ('npk!', 'cls!', 'pck!', 'prc!'):
            items = self._browse_action_container(
                action, items, join(storage['storage_id'], path), form)

        # Synchronize
        if not working:
            working = handler.synchronize(self._request, action == 'syn!')
            action = '' if working else action

        return form, action, items, working

    # -------------------------------------------------------------------------
    def _browse_action_create(self, storage, handler, path, action, form):
        """Manage actions for file or directory creation.

        :param storage: (dictionary)
            Storage dictionary.
        :param handler: (:class:`~..lib.handler.Handler` instance)
            Storage Control System.
        :param path:
            Relative path in storage.
        :param action: (string)
            Action.
        :param form: (:class:`~..lib.form.Form` instance)
            Browse form.
        :return: (boolean)
            ``True`` if work in progress.
        """
        working = False
        if action == 'new?' \
           and storage['seeds'] is not None and not storage['seeds']:
            storage['seeds'] = self._request.registry['opener'].seed_list(
                self._request, storage['openers'])
        elif action == 'new!':
            seed = self._request.registry['opener'].seed_fullpath(
                self._request, form.values['seed'])
            working = handler.launch(
                self._request, handler.create,
                (vcs_user(self._request, storage), seed, path,
                 form.values['new_name'], form.values.get(
                     'message',
                     get_localizer(self._request).translate(_('Creation')))))
        elif action == 'dir!':
            working = handler.launch(
                self._request, handler.mkdir,
                (vcs_user(self._request, storage), path,
                 form.values['directory'], form.values.get(
                     'message',
                     get_localizer(self._request).translate(_('Creation')))))
        return working

    # -------------------------------------------------------------------------
    def _browse_action_container(self, action, items, path, form):
        """Manage container actions.

        :param action: (string)
            Action.
        :param items: (list)
            List of selected items.
        :param path: (string)
            Relative path from storage root.
        :param form: (:class:`~..lib.form.Form` instance)
            Browse form.
        :return: (tuple)
            A tuple such as ``(project_id, pack_id)`` or ``items``
        """
        # Close container
        if action == 'cls!' and 'container' in self._request.session:
            del self._request.session['container']

        # Add to container
        elif action[0:4] in ('pck!', 'prc!'):
            add2container(
                self._request, action[0:3], action[4:7], path, items)
            form.forget('#')

        # Create pack
        elif action[0:4] == 'npk!':
            if 'project' in self._request.session \
                    and self._request.session['project']['perm'] \
                    in ('leader', 'packmaker'):
                return create_pack(self._request, items, path)
            form.forget('#')
            return [None]

        return items

    # -------------------------------------------------------------------------
    def _vcs_user_form(self, storage, action):
        """Create a VCS user form and, eventually, update ``StorageUser``
        table setting up ``vcs_user`` and ``vcs_password``.

        :param storage: (dictionary)
            Storage dictionary.
        :param action: (string)
            Current action
        :return: (:class:`~.lib.form.Form` instance)
        """
        schema = SchemaNode(Mapping())
        schema.add(SchemaNode(
            String(), name='vcs_user',
            validator=Length(max=ID_LEN), missing=None))
        schema.add(SchemaNode(String(), name='vcs_password', missing=None))
        if 'seed' in self._request.params:
            schema.add(SchemaNode(String(), name='seed'))
        if 'message' in self._request.params:
            schema.add(SchemaNode(
                String(), name='message',
                validator=Length(max=DESCRIPTION_LEN)))
        if 'directory' in self._request.params:
            schema.add(SchemaNode(
                String(), name='directory', validator=Length(max=PATH_LEN)))
        elif action[0:4] == 'ren?' or 'new_name' in self._request.params:
            schema.add(SchemaNode(
                String(), name='new_name', validator=Length(max=PATH_LEN)))

        form = Form(self._request, schema=schema)
        if action[0:4] == 'ren?':
            form.values['new_name'] = action[4:]
            return form
        if not form.validate() or 'vcs_change' not in self._request.params:
            return form

        save_vcs_user(self._request, storage)
        return form

    # -------------------------------------------------------------------------
    def _vcs_recover(self, storage):
        """Run a `recover` action on the current storage.

        :param storage: (:class:`~..lib.models.Storage` instance)
            Storage dictionary.
        """
        handler = self._request.registry['handler']\
            .get_handler(storage.storage_id, storage)
        handler.launch(self._request, handler.recover)
        self._request.session.flash(_('Recover has been launched.'))

    # -------------------------------------------------------------------------
    def _swap_openers(self, direction, opener_id, storage):
        """Swap two openers.

        :param direction: ('mup' or 'dwn')
            Direction of the move.
        :param opener_id: (string)
            ID of the opener to move.
        :param storage: (:class:`~..models.storage.Storage` instance)
            Current storage object.
        """
        # Something to do?
        opener_ids = [
            k.opener_id for k in sorted(storage.openers, key=lambda k: k.sort)]
        direction = direction == 'dwn' and 1 or -1
        index = opener_ids.index(opener_id)
        if (direction == -1 and index == 0) \
           or (direction == 1 and index + 1 == len(opener_ids)):
            return

        # Swap in database
        item1 = [k for k in storage.openers if k.opener_id == opener_id][0]
        item2 = opener_ids[index + direction]
        item2 = [k for k in storage.openers if k.opener_id == item2][0]
        item1.sort, item2.sort = item2.sort, item1.sort

        if 'storage' in self._request.session:
            del self._request.session['storage']
