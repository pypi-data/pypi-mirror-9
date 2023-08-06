# $Id: viewutils.py 828a3c221ecf 2014/12/09 15:00:26 Patrick $
"""Some various utilities for views."""

from os import walk
from os.path import exists, join, isfile, dirname, relpath, basename, normpath
import zipfile
import tempfile
from datetime import datetime, date
from sqlalchemy import select, desc, or_, and_
from colander import SchemaNode, Mapping, String, Integer, Boolean
from colander import All, Length, Regex, OneOf
from webhelpers2.html import literal
from lxml import etree

from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden
from pyramid.i18n import get_localizer
from pyramid.response import Response

from .utils import _, EXCLUDED_FILES, encrypt, decrypt, get_mime_type
from .utils import has_permission, hash_sha, camel_case, normalize_name
from .utils import normalize_spaces
from .xml import local_text
from .form import grid_item
from .widget import Paging
from ..models import NULL, ID_LEN, VALUE_LEN, DBSession
from ..models.users import User
from ..models.groups import GROUPS_USERS, Group
from ..models.storages import VCS_ENGINES, Storage, StorageUser, StorageGroup
from ..models.projects import Project, ProjectUser, ProjectGroup
from ..models.roles import Role, RoleUser
from ..models.processings import Processing, ProcessingFile
from ..models.tasks import Task
from ..models.packs import Pack, PackFile


VARIABLE_TYPES = {
    'string': _('String'), 'text': _('Text'), 'boolean': _('Boolean'),
    'integer': _('Integer'), 'regex': _('Regular expression'),
    'select': _('Closed list')}


# =============================================================================
def connect_user(request, code, password=None):
    """If the user with ``code`` and ``password`` is authorized, it updates
    ``last_login`` field in database and returns an ``User`` object.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param code: (string)
        Login of the user to connect.
    :param password: (string, optional)
        Clear password.
    :return: (:class:`~.models.users.User` instance or integer)
        The connected user or an error code.

    If ``password`` is ``None``, password checking is not performed.

    Values of the error code are:

    * 1: incorrect user code or password
    * 2: inactive account
    * 3: expired account
    * 4: forbidden IP
    """
    # Check user
    code = normalize_name(code)[0:ID_LEN]
    user = DBSession.query(User).filter_by(login=code).first()
    if user is None:
        return 1
    if password is not None:
        key = request.registry.settings.get('encryption', '-')
        if hash_sha(password.strip(), key) != user.password:
            return user.password is None and 2 or 1
    if user.status != 'active':
        return 2 if user.status == 'inactive' else 1
    if user.expiration and user.expiration < date.today():
        return 3
    if user.restrict_ip and not (
            request.environ['REMOTE_ADDR'] in [str(k.ip) for k in user.ips]):
        return 4

    # Update last login date in database
    user.last_login = datetime.now()
    DBSession.commit()
    return user


# =============================================================================
def get_action(request):
    """Return a tuple such as ``(action, items)`` where ``action`` is a
    string such as ``<act><?|!><item_id>`` and ``items`` is a list of
    selected items in a list form.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :return: (tuple)
        A tuple such as ``(action, items)``.

    Each submit button returns a string such as ``<act><?|!><item_id>.x`` where
    ``<item_id>`` is the item identifier or ``#`` for all selected items,
    ``<?|!>`` means respectively *confirm* or *proceed* and ``<act>`` is one of
    the following action:

    * ``agp``: add groups
    * ``aur``: add users
    * ``bld``: build
    * ``ccl``: cancel
    * ``cls``: close
    * ``del``: delete
    * ``drl``: delete role
    * ``dtk``: delete task
    * ``dvl``: delete value
    * ``des``: description
    * ``dif``: get diff
    * ``dir``: make directory
    * ``dnl``: download
    * ``dwn``: move down
    * ``dup``: duplicate
    * ``exp``: export
    * ``imp``: import
    * ``not``: modify a note
    * ``npk``: create a new pack with selection
    * ``ipk``: import pack with configuration and content
    * ``mup``: move up
    * ``new``: create a new object
    * ``nxt``: transition to next task
    * ``pck``: add to pack
    * ``prc``: add to processing
    * ``ren``: rename
    * ``rgp``: remove groups
    * ``rur``: remove users
    * ``rmv``: remove
    * ``sch``: search
    * ``shw``: show
    * ``syn``: synchronize
    * ``tak``: take
    * ``upl``: upload

    Checkbox inputs return string such as ``#<item_id>``.

    For instance, ``del!#`` and ``['#user1', '#user2']`` means "delete
    ``user1`` and ``user2``". ``syn!DataHg`` means "synchronize
    ``DataHg`` and only this one".
    """
    action = ''
    items = []
    for param in request.params:
        if not isinstance(param, unicode):
            param = param.decode('utf8')
        if param[0] == '#':
            items.append(param[1:])
        elif param[-2:] == '.x':
            if param[-3:-2] == '#':
                action = param[0:-2]
            else:
                return param[0:-2], (param[4:-2],)
    if '#' in action and not items:
        request.session.flash(_('Select items!'), 'alert')
        action = ''
    return action, items


# =============================================================================
def paging_users(request, only_active=True):
    """Return a :class:`~.widget.Paging` object filled with users.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param only_active: (boolean, default=True)
        if ``True``, only active users are included.
    :return: (tuple)
        A tuple such as ``(paging, filters)`` where ``paging`` is a
        :class:`~.widget.Paging` object and ``filters`` a dictionary of
        filters.
    """
    # Parameters
    paging_id = only_active and 'users' or 'users!'
    params = Paging.params(request, paging_id, '+name')
    if only_active or (len(request.POST) == 0 and 'f_status' not in params):
        params['f_status'] = 'active'

    # Query
    query = DBSession.query(User.user_id, User.login, User.name, User.status)
    if 'f_login' in params:
        query = query.filter(
            User.login.like('%%%s%%' % params['f_login'].lower()))
    if 'f_name' in params:
        query = query.filter(User.name.ilike('%%%s%%' % params['f_name']))
    if 'f_status' in params and params['f_status'] != '*':
        query = query.filter(User.status == params['f_status'])
    if 'f_group' in params:
        query = query.join(GROUPS_USERS).filter(
            GROUPS_USERS.c.group_id == params['f_group'])

    # Order by
    oby = 'users.%s' % params['sort'][1:]
    query = query.order_by(desc(oby) if params['sort'][0] == '-' else oby)

    return Paging(request, paging_id, query), params


# =============================================================================
def paging_groups(request, paging_id='groups'):
    """Return a :class:`~.widget.Paging` object filled with groups.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param paging_id: (string, default='groups')
        Paging ID: ``'groups'`` for adding purpose and ``groups!`` for
        administrationg purpose.
    :return: (tuple)
        A tuple such as ``(paging, filters)`` where ``paging`` is a
        :class:`~.widget.Paging` object and ``filters`` a dictionary of
        filters.
    """
    # Parameters
    params = Paging.params(request, paging_id, '+label')

    # Query
    query = DBSession.query(Group)
    if 'f_label' in params:
        query = query.filter(Group.label.ilike('%%%s%%' % params['f_label']))

    # Order by
    oby = 'groups.%s' % params['sort'][1:]
    query = query.order_by(desc(oby) if params['sort'][0] == '-' else oby)

    return Paging(request, paging_id, query), params


# =============================================================================
def current_storage(request, storage_id=None, only_dict=True):
    """Initialize, if necessary, ``request.session['storage']`` and
    return it as current storage dictionary.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param storage_id: (integer, optional)
        ID of storage to get context.
    :param only_dict: (boolean, default=True)
        If ``False``, it returns the entire
        :class:`~.models.storages.Storage` object.
    :return: (tuple)
        A tuple such as ``(storage_dictionary, handler)`` or
        ``(storage_object, handler)`` or a
        :class:`pyramid.httpexceptions.`HTTPNotFound` exception.

    ``storage_dictionary`` has the following keys: ``storage_id``,
    ``label``, ``description``, ``perm``, ``vcs_engine``, ``vcs_url``,
    ``public_url``, ``indexed``.
    """
    # Already in session
    storage_id = storage_id or request.matchdict.get('storage_id')
    if storage_id is None:
        raise HTTPNotFound(comment=_('You must specify a storage ID!'))
    if only_dict and 'storage' in request.session and request\
            .session['storage']['storage_id'] == storage_id:
        handler = request.registry['handler'].get_handler(storage_id)
        if handler is not None:
            return request.session['storage'], handler

    # Read in database
    storage = DBSession.query(Storage).filter_by(
        storage_id=storage_id).first()
    if storage is None:
        raise HTTPNotFound(comment=_('This storage does not exist!'))

    # Permission
    user_id = request.session['user_id']
    perm = (has_permission(request, 'stg_editor') or storage.access == 'open')\
        and 'writer' or None
    if perm != 'writer':
        record = DBSession.query(StorageUser).filter_by(
            storage_id=storage_id, user_id=user_id).first()
        perm = record and record.perm or None
    if perm != 'writer':
        groups = [k.group_id for k in DBSession.execute(
            select([GROUPS_USERS], GROUPS_USERS.c.user_id == user_id))]
        if groups:
            record = [
                k[0] for k in DBSession.query(StorageGroup.perm)
                .filter(StorageGroup.storage_id == storage_id)
                .filter(StorageGroup.group_id.in_(groups))]
            perm = ('writer' in record and 'writer') or (record and record[0])\
                or perm
    if perm is None:
        raise HTTPForbidden(comment=_(
            'You do not have access to this storage!'))

    # Openers
    openers = [
        k.opener_id for k in sorted(storage.openers, key=lambda k: k.sort)]

    request.session['storage'] = {
        'storage_id': storage_id,
        'label': storage.label,
        'description': storage.description,
        'perm': perm,
        'vcs_engine': VCS_ENGINES[storage.vcs_engine],
        'vcs_url': storage.vcs_url,
        'public_url': storage.public_url,
        'indexed': bool(storage.indexed_files),
        'openers': openers,
        'seeds':
            tuple() if request.registry['opener'].has_seeds(openers) else None}
    handler = request.registry['handler'].get_handler(storage_id, storage)
    return only_dict and (request.session['storage'], handler) \
        or (storage, handler)


# =============================================================================
def query_storages(query, user_id, with_index=False):
    """Return the query to find storages of a user.

    :param query: (:class:`sqlalchemy.orm.query.Query` instance)
        Current query to update.
    :param user_id: (integer)
        Current user_id
    :param with_index: (boolean, default=False)
        If ``True`` select only storages with indexed files.
    :return: (:class:`sqlalchemy.orm.query.Query` instance)
    """
    groups = [k.group_id for k in DBSession.execute(
        select([GROUPS_USERS], GROUPS_USERS.c.user_id == user_id))] \
        if DBSession.query(StorageGroup).first() else None
    if groups:
        query = query.filter(or_(
            Storage.access == 'open',
            and_(StorageUser.user_id == user_id,
                 StorageUser.perm != NULL,
                 StorageUser.storage_id == Storage.storage_id),
            and_(StorageGroup.group_id.in_(groups),
                 StorageGroup.storage_id == Storage.storage_id)))\
            .distinct(Storage.storage_id, Storage.label)
    else:
        query = query.join(StorageUser).filter(or_(
            Storage.access == 'open',
            and_(StorageUser.user_id == user_id, StorageUser.perm != NULL)))\
            .distinct(Storage.storage_id, Storage.label)
    if with_index:
        query = query.filter(Storage.indexed_files != NULL)
    return query


# =============================================================================
def vcs_user(request, storage):
    """Return a VCS user tuple.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param storage: (dictionary)
        Storage dictionary.
    :return: (tuple)
        A VCS user tuple ``(user_id, password, name)``.
    """
    user = DBSession.query(StorageUser).filter_by(
        storage_id=storage['storage_id'],
        user_id=request.session['user_id']).first()
    if user is None:
        return None, None, request.session['name']
    password = decrypt(
        user.vcs_password, request.registry.settings.get('encryption', '-'))
    return user.vcs_user, password, request.session['name']


# =============================================================================
def save_vcs_user(request, storage):
    """Save user name and password for VCS in database.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param storage: (dictionary)
        Storage dictionary.
    """
    if not request.params.get('vcs_user'):
        return
    user = DBSession.query(StorageUser).filter_by(
        storage_id=storage['storage_id'],
        user_id=request.session['user_id']).first()
    if user is None:
        user = StorageUser(
            storage['storage_id'], user_id=request.session['user_id'])
    user.vcs_user = request.params['vcs_user']
    user.vcs_password = encrypt(
        request.params.get('vcs_password'),
        request.registry.settings.get('encryption', '-'))
    DBSession.commit()
    request.session.flash(_('VCS user has been changed.'))


# =============================================================================
def file_details(request, record, only_visible=True):
    """Return a dictionary of details on file contained in ``record``.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param record: (:class:`~.models.processings.Processing`
        or :class:`~.models.packs.Pack` instance).
    :param only_visible: (boolean, default=True)
        If ``True``, it returns a list of only visible files otherwise it
        returns a dictionary.
    :return: (dictionary)
        A dictionary with keys ``file``, ``resource`` and ``template``. Each
        value of this dictionary is a tuple of tuples such as ``(file_type,
        storage_id, path, target, visible)``.
    """
    files = {'file': [], 'resource': [], 'template': []}
    if record is None:
        return files

    root_path = request.registry.settings['storage.root']
    for item in sorted(record.files, key=lambda k: k.sort):
        if not only_visible or (hasattr(item, 'visible') and item.visible):
            files[item.file_type].append((
                get_mime_type(join(root_path, item.path))[1],
                item.path.partition('/')[0], item.path.partition('/')[2],
                item.target, hasattr(item, 'visible') and item.visible))

    return files


# =============================================================================
def file_download(request, path, filenames, download_name=None):
    """Prepare file for download and return a Pyramid response.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param path: (string)
        Absolute path to files.
    :param filenames: (list)
        List of files to download.
    :param download_name: (string)
        Visible name during download.
    :return: (:class:`pyramid.response.Response` instance or raise a
        :class:`pyramid.httpexceptions.HTTPNotFound` exception.)
    """
    # Single file
    fullname = join(path, filenames[0])
    if len(filenames) == 1 and isfile(fullname):
        with open(fullname, 'rb') as hdl:
            content = hdl.read()
        download_name = download_name or basename(filenames[0])
        response = Response(content, content_type=get_mime_type(fullname)[0])
        response.headerlist.append((
            'Content-Disposition',
            'attachment; filename="%s"' % download_name.encode('utf8')))
        return response

    # Several files
    tmp = tempfile.NamedTemporaryFile(
        dir=request.registry.settings['temporary_dir'])
    zip_file = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
    for name in filenames:
        fullname = normpath(join(path, name))
        if not fullname.startswith(path) or not exists(fullname):
            zip_file.close()
            raise HTTPNotFound(comment=_('This file does not exist!'))
        if isfile(fullname):
            try:
                zip_file.write(fullname, name)
            except zipfile.LargeZipFile:
                zip_file.close()
                raise HTTPForbidden(comment=_('This file is too big!'))
            continue
        for root, dirs, files in walk(fullname):
            for name in dirs:
                if name in EXCLUDED_FILES:
                    dirs.remove(name)
            for name in files:
                if name not in EXCLUDED_FILES:
                    name = join(root, name)
                    try:
                        zip_file.write(name, relpath(name, path))
                    except zipfile.LargeZipFile:
                        zip_file.close()
                        raise HTTPForbidden(comment=_('This file is too big!'))
                    except IOError as error:
                        zip_file.close()
                        raise HTTPNotFound(comment=error)
    zip_file.close()
    download_name = download_name or '%s.zip' % (
        len(filenames) == 1 and basename(filenames[0]) or basename(path))
    return file_download(request, '', (tmp.name,), download_name)


# =============================================================================
def file_upload(request, path, message):
    """Update a file in a storage.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param path: (string)
        Path of the file to update starting with storage ID.
    :param message: (string)
        Message for commit.
    :return: (boolean)
        ``True`` if operation still in progress.
    """
    path = path.split('/')
    storage_id = path[0]
    path = path[1:]
    upload_file = request.params.get('upload_file')
    if upload_file is None or isinstance(upload_file, basestring) or not path:
        return False

    storage, handler = current_storage(request, storage_id)
    if storage['perm'] != 'writer':
        request.session.flash(_("You can't modify this storage!"), 'alert')
        return False
    if path[-1] != upload_file.filename:
        request.session.flash(_('File names are different.'), 'alert')
        return False

    working = handler.upload(
        vcs_user(request, storage), join('.', *path[0:-1]),
        upload_file, path[-1], message)
    if handler.progress()[0] == 'error':
        request.session.flash(handler.progress()[1], 'alert')
    else:
        request.session.flash(_('File has been updated.'))

    return working


# =============================================================================
def add2container(request, container_type, file_type, path, filenames):
    """Add files to a processing or a pack.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param container_type: ('prc' or 'pck')
        ``'prc'`` for processing and ``'pck'`` for pack.
    :param file_type: ('fil', 'rsc', 'tpl', 'out')
        ``'fil'`` for file,``'rsc'`` for resource, ``'tpl'`` for template and
        ``'out'`` for output directory.
    :param path:
        Relative path from storage root.
    :param filenames: (list)
        Names of files to add.
    """
    if 'container' not in request.session:
        return
    project_id = request.session['container']['project_id']
    file_type = {'fil': 'file', 'rsc': 'resource', 'tpl': 'template',
                 'out': 'output'}[file_type]
    # Output
    if file_type == 'output':
        if len(filenames) > 1:
            request.session.flash(_('Select only one directory!'), 'alert')
            return
        name = join(
            request.registry.settings['storage.root'], path, filenames[0])
        name = dirname(filenames[0]) if isfile(name) else filenames[0]
        record = DBSession.query(Processing).filter_by(
            project_id=project_id, processing_id=request
            .session['container']['processing_id']).first()
        if record is not None:
            record.output = normpath(join(path, name))
            DBSession.commit()
            request.session.flash(_(
                'Output directory has been changed to "${n}".',
                {'n': record.output}), 'message')
        return

    # Container
    if container_type == 'pck':
        record = DBSession.query(Pack).filter_by(
            project_id=project_id,
            pack_id=request.session['container']['pack_id']).first()
        container_class = PackFile
    else:
        record = DBSession.query(Processing).filter_by(
            processing_id=request.session['container']['processing_id'],
            project_id=project_id).first()
        container_class = ProcessingFile
    if record is None:
        return
    paths = [k.path for k in record.files if k.file_type == file_type]

    # Browse files
    added = []
    for name in filenames:
        name = normpath(join(path, name))
        if name in paths:
            continue
        record.files.append(container_class(file_type, name))
        added.append(name)
    if container_type == 'pck':
        record.updated = datetime.now()
    record.update_sort()
    DBSession.commit()

    # Current task
    if container_type == 'pck' and 'task' in request.session \
            and request.session['task']['pack_id'] == record.pack_id:
        request.session['task']['files'] = file_details(request, record)

    # Message
    if len(added) > 0:
        record = {'a': ', '.join(added)}
        added = {
            'file': _('Files to process added: ${a}', record),
            'resource': _('Resource files added: ${a}', record),
            'template': _('Template files added: ${a}', record)
        }[file_type]
        request.session.flash(added, 'message')


# =============================================================================
def current_project(request, project_id=None, only_dict=True):
    """Update ``request.session['project']`` and return it as current project
    dictionary or return a SqlAlchemy object.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param project_id: (integer, optional)
        ID of project to get context.
    :param only_dict: (boolean, default=True)
        If ``False``, it returns the entire :class:`~.models.projects.Project`
        object.
    :return: (dictionary, :class:`~.models.projects.Project` or ``None``)
        ``None`` if error. Dictionary has the following keys:
        ``project_id``, ``label``, ``description``, ``deadline``, ``entries``,
        ``perm``, ``role_labels``, ``my_roles``, ``processing_labels``,
        ``task_labels`` and ``processing_id`` (default processing ID),.
    """
    # Already in session
    project_id = project_id or request.matchdict.get('project_id') \
        or request.matchdict.get('build_id', '').partition('-')[0] \
        or None
    if project_id is None:
        raise HTTPNotFound(comment=_('You must specify a project ID!'))
    project_id = int(project_id)
    if 'project' in request.session \
            and request.session['project']['project_id'] == project_id:
        if request.params.get('processing_id'):
            request.session['project']['processing_id'] = \
                int(request.params['processing_id'])
        if only_dict:
            return request.session['project']

    # Read in database
    project = DBSession.query(Project).filter_by(project_id=project_id).first()
    if project is None:
        raise HTTPNotFound(comment=_('This project does not exist!'))
    if 'project' in request.session \
            and request.session['project']['project_id'] == project_id:
        return project

    # Cleanup
    if 'task' in request.session:
        del request.session['task']

    # Project dictionary
    project_dict = {
        'project_id': project_id, 'label': project.label,
        'description': project.description, 'deadline': project.deadline}

    # Permission
    user_id = request.session['user_id']
    record = DBSession.query(ProjectUser).filter_by(
        project_id=project_id, user_id=user_id).first()
    project_dict['entries'] = record and record.entries or 'all'
    project_dict['perm'] = record and record.perm or None
    if project_dict['perm'] != 'leader':
        groups = [k.group_id for k in DBSession.execute(
            select([GROUPS_USERS], GROUPS_USERS.c.user_id == user_id))]
        if groups:
            levels = {'member': 1, 'packmaker': 2, 'leader': 3}
            record = [
                '%d%s' % (levels[k[0]], k[0])
                for k in DBSession.query(ProjectGroup.perm)
                .filter(ProjectGroup.project_id == project_id)
                .filter(ProjectGroup.group_id.in_(groups))]
            project_dict['perm'] = record and max(record)[1:] \
                or project_dict['perm']
    if project_dict['perm'] != 'leader' \
            and has_permission(request, 'prj_editor'):
        project_dict['perm'] = 'packmaker'
    if project_dict['perm'] is None:
        raise HTTPForbidden(comment=_('You do not work in this project!'))

    # Project dictionary (continuation)
    project_dict['role_labels'] = dict(DBSession.query(
        Role.role_id, Role.label).filter_by(project_id=project_id).all())
    project_dict['my_roles'] = tuple([
        k[0] for k in DBSession.query(RoleUser.role_id)
        .filter_by(project_id=project_id, user_id=user_id)])
    project_dict['processing_labels'] = tuple(
        DBSession.query(Processing.processing_id, Processing.label)
        .filter_by(project_id=project_id).order_by(Processing.label).all())
    project_dict['task_labels'] = dict(DBSession.query(
        Task.task_id, Task.label).filter_by(project_id=project_id).all())
    project_dict['processing_id'] = int(request.params.get('processing_id', 1))

    request.session['project'] = project_dict
    return only_dict and request.session['project'] or project


# =============================================================================
def current_processing(
        request, project_id=None, processing_id=None, container=False):
    """Return the current processing object.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param project_id: (integer, optional)
        ID of project to retrieve processing.
    :param processing_id: (integer, optional)
        ID of processing to retrieve.
    :param container: (boolean)
        If ``True``, add current processing container.
    :return: (tuple)
        A tuple such as ``(processing, processor, output)``.

    ``processing`` is a :class:`~.models.processings.Processing`
    object. ``processor`` is a :class:`lxml.etree.ElementTree` object
    representing the used processor. ``output`` is a dictionary with keys
    ``storage_id``, ``storage_label`` and ``path``.

    If this function fails, it raises a
    :class:`pyramid.httpexceptions.`HTTPNotFound` exception.

    ``request.session['container']`` is updated with ``processing_id``,
    ``processing_label`` and ``has_output``.
    """
    # IDs
    project_id = project_id or request.matchdict.get('project_id')
    if project_id is None:
        raise HTTPNotFound(comment=_('You must specify a project ID!'))
    processing_id = processing_id or request.matchdict.get('processing_id')
    if processing_id is None:
        raise HTTPNotFound(comment=_('You must specify a processing ID!'))
    project_id = int(project_id)
    processing_id = int(processing_id)

    # Processing
    processing = DBSession.query(Processing).filter_by(
        project_id=project_id, processing_id=processing_id).first()
    if processing is None:
        raise HTTPNotFound(comment=_('This processing does not exist!'))

    # Container for storage
    if container:
        request.session['container'] = {
            'project_id': project_id,
            'processing_id': processing_id,
            'processing_label': processing.label,
            'has_output': bool(processing.output)}

    # Processor
    processor = request.registry['fbuild'].processor(
        request, processing.processor)
    if processor is None:
        raise HTTPNotFound(comment=_(
            'Unknown processor "${p}"!', {'p': processing.processor}))
    processings = None
    for var in processor\
            .findall('processor/variables/group/var[@type="processing"]'):
        if processings is None:
            processings = dict([
                ('prc%d.%d' % (k.project_id, k.processing_id), k.label)
                for k in DBSession.query(Processing)
                .filter_by(project_id=project_id)
                if not k.processor.startswith('Parallel')])
        var.set('type', 'select')
        for k in sorted(processings, reverse=True):
            elt = etree.Element('option', value=k)
            elt.text = processings[k]
            var.insert(0, elt)
        elt = etree.Element('option', value='-')
        elt.text = ''
        var.insert(0, elt)

    # Output
    if not processing.output:
        return processing, processor, None
    storage_id = processing.output.partition('/')[0]
    storage = DBSession.query(Storage).filter_by(storage_id=storage_id).first()
    output = {
        'storage_id': storage_id,
        'storage_label': storage and storage.label or storage_id,
        'path': processing.output.partition('/')[2]}

    if '%(user)s' in output['path']:
        login = DBSession.query(User.login).filter_by(
            user_id=request.session['user_id']).first()[0]
        output['path'] = output['path'].replace('%(user)s', camel_case(login))

    return processing, processor, output


# =============================================================================
def variable_schema(processor, values, with_visibility=True):
    """Return a schema to validate variable form.

    :param processor: (:class:`lxml.etree.ElementTree` instance)
        Processor of current processing.
    :param values: (dictionary)
        Values affected to variables.
    :param with_visibility: (boolean, default=True)
        If ``True``, create schema for visibility.
    :return: (tuple)
        A tuple such as ``(schema, defaults)`` where ``schema`` is a
        :class:`colander.SchemaNode` instance and ``defaults`` a dictionary.
    """
    schema = SchemaNode(Mapping())
    defaults = {}
    for var in processor.findall('processor/variables/group/var'):
        name = var.get('name')
        if name not in values:
            continue
        schema.add(variable_schema_node(name, var.get('type'), var))
        defaults[name] = \
            values[name][0] if values[name][0] is not None \
            else var.findtext('default') is not None \
            and var.findtext('default').strip() or ''
        if var.get('type') == 'boolean':
            defaults[name] = (defaults[name] == 'true')
        elif var.get('type') == 'string':
            defaults[name] = normalize_spaces(defaults[name])
        if with_visibility:
            schema.add(
                SchemaNode(Boolean(), name='%s_see' % name, missing=False))
            defaults['%s_see' % name] = values[name][1]

    return schema, defaults


# =============================================================================
def variable_schema_node(name, var_type, var=None):
    """Return a SchemaNode according to ``var_type``.

    :param name: (string)
         Name of the variable.
    :param var_type: (string)
         Type of the variable.
    :param var: (:class:`lxml.etree.Element` instance, optional)
         Variable node.
    :return: (:class:`colander.SchemaNode` instance)
    """
    if var_type == 'boolean':
        node = SchemaNode(Boolean(), name=name, missing=False)
    elif var_type == 'integer':
        node = SchemaNode(Integer(), name=name, missing=0)
    elif var_type == 'select' and var is not None:
        options = [k.get('value', k.text) for k in var.findall('option')]
        node = SchemaNode(String(), name=name, validator=OneOf(options))
    elif var_type == 'regex' and var is not None:
        regex = '^%s$' % var.findtext('pattern').strip()
        node = regex[1] == '(' and regex[-3:] == ')?$' \
            and SchemaNode(String(), name=name, validator=All(
                Regex(regex), Length(max=VALUE_LEN)), missing='') \
            or SchemaNode(String(), name=name, validator=All(
                Regex(regex), Length(max=VALUE_LEN)))
    elif var_type == 'text':
        node = SchemaNode(String(), name=name, missing='')
    else:
        node = SchemaNode(
            String(), name=name, validator=Length(max=VALUE_LEN),
            missing='')
    return node


# =============================================================================
def variable_input(form, name, var_type, var=None, **attrs):
    """Return an input tag for the variable ``name``.

    :param form: (:class:`~.form.Form` instance)
         Current form.
    :param name: (string)
         Name of the variable.
    :param var_type: (string)
         Type of the variable.
    :param var: (:class:`lxml.etree.Element` instance, optional)
         Variable node.
    :param attrs: (dictionary)
         Keyworded arguments for ``webhelpers2.html.tags`` object.
    :return: (one of :class:`~.form.Form` tag instance)
    """
    cast = var is not None and var.get('cast') or None
    if cast:
        attrs['data-cast'] = cast
    class_ = var is not None and var.get('class') or None
    class_ = class_ and '%s%s' % (class_, cast and ' cast-%s' % cast or '') \
        or cast and 'cast-%s' % cast or None
    if var_type == 'boolean':
        tag = form.checkbox(name, class_=class_, **attrs)
    elif var_type == 'text' and var is not None:
        tag = form.textarea(
            name, rows=min(int(var.get('rows', '6')), 45), cols=80,
            class_=class_, **attrs)
    elif var_type == 'text':
        tag = form.textarea(name, rows=6, cols=80, class_=class_, **attrs)
    elif var_type == 'select' and var is not None:
        tag = form.select(
            name, None,
            [(k.get('value', k.text), k.text) for k in var.findall('option')],
            class_=class_, **attrs)
    else:
        tag = form.text(name, class_=class_, **attrs)
    return tag


# =============================================================================
def variable_description(request, variables, name, values=None,
                         processor_default=False, default=False):
    """Return a description of variable ``name``.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param variables: (:class:`lxml.etree.Element` instance)
        <variables> DOM object.
    :param name: (string)
        Name of the variable.
    :param values: (dictionary, optional)
        Values affected to the variables.
    :param processor_default: (boolean, default=False)
        Show the processor default value if any.
    :param default: (boolean, default=False)
        Show the processing default value.
    :return: (string)
    """
    if variables is None:
        return
    var = variables.xpath('variables/group/var[@name="%s"]' % name)
    if not len(var):
        return
    var = var[0]
    translate = get_localizer(request).translate

    # Label/name
    text = name
    if var.find('label') is not None:
        text = '%s (%s)' % (local_text(var, 'label', request), name)
    html = grid_item(translate(_('Name:')), text, class_='')

    # Type
    text = translate(VARIABLE_TYPES[var.get('type')])
    if var.get('type') == 'regex':
        text += ' %s' % var.findtext('pattern')
    html += grid_item(translate(_('Type:')), text, class_='')

    # Value
    if values is not None and name in values:
        text = values[name][2] \
            and values[name][2] != values[name][0] \
            and '%s (%s)' % (values[name][2], values[name][0]) \
            or values[name][0]
        html += grid_item(translate(_('Value:')), text, class_='')

    # Factory value
    if processor_default and var.findtext('default') is not None:
        html += grid_item(
            translate(_('Factory:')), var.findtext('default'), class_='')

    # Default value
    if default and values is not None:
        html += grid_item(
            translate(_('Default:')), values[name][1], class_='')

    # Description
    description = ''
    if var.find('description') is not None:
        description += local_text(
            var, 'description', request).replace(' --', '<br/>')
    if var.getparent().find('description') is not None:
        description += description and '<br/><br/>' or ''
        description += local_text(
            var.getparent(), 'description', request).replace(' --', '<br/>')
    if description:
        html += grid_item(
            translate(_('Description:')), literal(description), class_='')

    return html


# =============================================================================
def task_auto_build(request, pack, task=None):
    """Launch build for a task of type `auto`.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param pack: (:class:`~.models.packs.Pack` instance)
        Current pack object.
    :param task: (:class:`~.models.tasks.Task` instance, optional)
        Current task for pack.
    :return: (boolean)
        ``True`` if build is  successfully launched.
    """
    # Task
    if task is None:
        task = DBSession.query(Task).filter_by(
            project_id=pack.project_id, task_id=pack.task_id).first()
    if task is None or not len(task.processings):
        return True

    # Back and next
    task_ko = [k for k in task.links if k.link_type == 'back']
    task_ko = len(task_ko) and task_ko[0].target_id or None
    task_ok = [k for k in task.links if k.link_type != 'back']
    task_ok = len(task_ok) \
        and '%d#%s' % (task_ok[0].target_id, task_ok[0].link_type) \
        or None

    # Launch build
    processing, processor = current_processing(
        request, project_id=task.project_id,
        processing_id=task.processings[0].processing_id)[0:2]
    front_build = request.registry['fbuild'].start_build(
        request, processing, processor, pack, (task_ko, task_ok))
    return front_build is not None


# =============================================================================
def operator_label(request, project, operator_type, operator_id):
    """Return localized operator label.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param project: (dictionary)
        Current project dictionary.
    :param operator_type: (string)
        Operator type.
    :param operator_id: (integer)
        Operator ID.
    :return: (string)
    """
    if operator_type == 'role':
        label = get_localizer(request).translate(_(
            '[Role] ${l}', {'l': project['role_labels'].get(operator_id, '')}))
    elif operator_type == 'user':
        label = DBSession.query(User.name).filter_by(
            user_id=operator_id).first()
        label = label and label[0] or ''
    else:
        label = get_localizer(request).translate(_('[Automatic]'))
    return label


# =============================================================================
def operator_labels(project, with_auto=False):
    """Return a list of all operators of the project ``project``.

    :param project: (dictionary)
        Current project dictionary.
    :param with_auto: (boolean)
        If ``True`` add automatic operator in the list.
    :return: (list)
    """
    operators = Project.team_query(project['project_id'])\
        .order_by('users.name').all()
    operators = [
        ('role%d' % k[0], _('[Role] ${l}', {'l': k[1]}))
        for k in project['role_labels'].items()] \
        + [('user%d' % k[0], k[2]) for k in operators]
    if with_auto:
        operators = [('autoNone', _('[Automatic]'))] + operators
    return operators
