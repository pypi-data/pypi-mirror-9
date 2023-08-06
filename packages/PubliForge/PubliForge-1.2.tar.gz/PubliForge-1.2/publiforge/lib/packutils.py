# $Id: packutils.py d3ec2ad35f84 2014/08/10 18:12:19 Patrick $
"""Some various utilities for packs."""
# pylint: disable = locally-disabled, C0302

from os import walk, sep
from os.path import exists, join, isfile, dirname, relpath, basename, normpath
from os.path import splitext
import tempfile
import zipfile
from lxml import etree
from sqlalchemy import desc

from pyramid.httpexceptions import HTTPNotFound

from .utils import _, EXCLUDED_FILES, normalize_name, normalize_spaces, decrypt
from .utils import has_permission
from .viewutils import file_download, current_project
from .viewutils import task_auto_build, operator_label
from .xml import PUBLIFORGE_RNG_VERSION, load
from ..models import LABEL_LEN, DBSession
from ..models.roles import Role
from ..models.storages import Storage, StorageUser
from ..models.tasks import Task
from ..models.packs import Pack, PackFile, PackEvent


# =============================================================================
def create_pack(request, filenames, path='.'):
    """Create a new pack with selected files.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param filenames: (list)
        Names of files to add to new pack.
    :param path: (string, optional)
        Common path.
    :return: (tuple)
        A tuple such as ``(project_id, pack_id``) or ``(None, None)`` if
        failed.
    """
    label = ', '.join([splitext(basename(k))[0] for k in filenames])
    project_id = request.session['project']['project_id']
    if DBSession.query(Pack) \
            .filter_by(project_id=project_id, label=label).first():
        request.session.flash(_('This pack already exists.'), 'alert')
        return None, None

    pack = Pack(project_id, label)
    for name in filenames:
        pack.files.append(
            PackFile('file', normpath(join(path, name))))
    DBSession.add(pack)
    DBSession.commit()
    return pack.project_id, pack.pack_id


# =============================================================================
def pack2task(request, pack, link_type, target_task_id):
    """Move pack ``pack`` to task with ID ``target_task_id``.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param pack: (:class:`~..models.packs.Pack` instance)
        Pack object.
    :param link_type: (string)
        Type of link: ``normal``, ``kept`` or ``back``.
    :param target_task_id: (integer)
        Task ID. If ``None``, the first non ``auto`` task is used.
    """
    # Find the new operator and, eventually, the new task ID
    operator = None
    if link_type == 'kept' and pack.operator_id is not None:
        operator = (pack.operator_type, pack.operator_id)
    elif link_type in ('back', 'kept', 'redo'):
        event = DBSession.query(
            PackEvent.task_id, PackEvent.operator_type, PackEvent.operator_id)\
            .filter_by(project_id=pack.project_id, pack_id=pack.pack_id)\
            .filter(PackEvent.operator_type != 'auto')
        if link_type in ('back', 'redo') and target_task_id:
            event = event.filter_by(task_id=target_task_id)
        event = event.order_by(desc('begin')).first()
        if event:
            target_task_id = target_task_id or event[0]
            operator = (event[1], event[2])

    # Find the new task
    if not target_task_id:
        return
    task = DBSession.query(Task).filter_by(
        project_id=pack.project_id, task_id=target_task_id).first()
    if task is None:
        return

    # Move pack to task
    old_pack = (pack.task_id, pack.operator_type, pack.operator_id)
    pack.task_id = task.task_id
    pack.operator_type = operator is not None and operator[0] \
        or task.operator_type
    pack.operator_id = operator is not None and operator[1] \
        or task.operator_id

    # Add event
    project = current_project(request)
    operator = operator_label(
        request, project, pack.operator_type, pack.operator_id)
    event = PackEvent(
        pack.project_id, pack.pack_id, pack.task_id,
        project['task_labels'][pack.task_id], pack.operator_type,
        pack.operator_id, operator)
    DBSession.add(event)
    DBSession.commit()

    # Automatic task
    if pack.operator_type == 'auto' \
            and not task_auto_build(request, pack, task):
        DBSession.query(PackEvent).filter_by(
            project_id=event.project_id, pack_id=event.pack_id,
            begin=event.begin).delete()
        pack.task_id = old_pack[0]
        pack.operator_type = old_pack[1]
        pack.operator_id = old_pack[2]
        DBSession.commit()


# =============================================================================
def pack_download(request, project_id, pack_id):
    """Download files of a pack in a ZIP file.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param project_id: (string)
        ID of pack to download.
    :param pack_id: (string)
        ID of pack to download.
    :return: (:class:`pyramid.response.Response` instance or raise a
        :class:`pyramid.httpexceptions.HTTPNotFound` exception.)
    """
    pack = DBSession.query(Pack).filter_by(
        project_id=project_id, pack_id=pack_id).first()
    if pack is None:
        raise HTTPNotFound(comment=_('Unknown pack!'))
    storage_root = request.registry.settings['storage.root']
    done = set(['pack.xml'])

    def _add_directory(zip_file, dirpath):
        """Add all files of a directory."""
        for root, name, files in walk(dirpath):
            for name in files:
                name = relpath(join(root, name), storage_root)
                if name not in done:
                    zip_file.write(join(storage_root, name), name)
                    done.add(name)

    # Create ZIP
    tmp = tempfile.NamedTemporaryFile(
        dir=request.registry.settings['temporary_dir'])
    zip_file = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)

    # Add meta data
    root = etree.Element('publiforge', version=PUBLIFORGE_RNG_VERSION)
    root.append(pack.xml())
    zip_file.writestr(
        'pack.xml', etree.tostring(
            root, encoding='utf-8', xml_declaration=True, pretty_print=True))

    # Add files
    for pfile in pack.files:
        if pfile.path not in done:
            path = join(storage_root, pfile.path)
            if isfile(path):
                zip_file.write(path, pfile.path)
            else:
                _add_directory(zip_file, path)
            done.add(pfile.path)
    zip_file.close()

    name = '%s.pfpck.zip' % normalize_name(pack.label)
    return file_download(request, '', (tmp.name,), name.decode('utf8'))


# =============================================================================
def pack_upload_settings(request, project_id, pack_doc=None, pack_id=None):
    """Import pack settings.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param project_id: (string)
        Current project ID.
    :param pack_doc: (:class:`lxml.etree.ElementTree` instance, optional)
        Pack XML DOM.
    :param pack_id: (integer, optional)
        Forced pack ID.
    """
    # pylint: disable = locally-disabled, E1103
    # Read content
    if pack_doc is None:
        upload = request.params.get('pack_file')
        if isinstance(upload, basestring):
            return
        if splitext(upload.filename)[1] != '.xml':
            request.session.flash(_('Incorrect file type!'), 'alert')
            return
        pack_doc = load(
            'pack.xml',
            {'publiforge':
             join(dirname(__file__), '..', 'RelaxNG', 'publiforge.rng')},
            upload.file.read())
        upload.file.close()
        if isinstance(pack_doc, basestring):
            request.session.flash(pack_doc, 'alert')
            return

    # Upload configurations
    roles = dict([
        ('rol%d.%d' % (project_id, k[0]), k[0]) for k
        in DBSession.query(Role.role_id).filter_by(project_id=project_id)])
    tasks = dict([
        ('tsk%d.%d' % (project_id, k[0]), k[0]) for k
        in DBSession.query(Task.task_id).filter_by(project_id=project_id)])
    packs = pack_doc.xpath('pack|packs/pack')
    for elt in pack_doc.xpath('pack|packs/pack'):
        pack = Pack.load(
            project_id, roles, tasks, elt,
            request.registry.settings['storage.root'], pack_id)
        if isinstance(pack, basestring):
            request.session.flash(pack, 'alert')
        elif len(packs) == 1:
            request.session['container'] = {
                'project_id': project_id,
                'pack_id': pack.pack_id, 'pack_label': pack.label}


# =============================================================================
def pack_upload_content(request, project_id, message, label=None,
                        handler=None):
    """Import pack content.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param project_id: (string)
        Current project ID.
    :param message: (string)
        Message for version control system.
    :param label: (string, optional)
        Label of pack to replace. If ``None``, the pack must be a new one.
    :param handler: (file handler, optional)
        File handler.
    :return: (``None`` or :class:`pyramid.i18n.TranslationString`)
    """
    # Check parameters
    if handler is None:
        upload = request.params.get('pack_file')
        if isinstance(upload, basestring):
            return
        handler = upload.file
    if not message:
        error = _('Message is required!')
        request.session.flash(error, 'alert')
        return error
    if not zipfile.is_zipfile(handler):
        error = _('Incorrect ZIP file!')
        request.session.flash(error, 'alert')
        return error
    zip_file = zipfile.ZipFile(handler, 'r')

    # Read "pack.xml"
    pack_doc = load(
        'pack.xml',
        {'publiforge':
         join(dirname(__file__), '..', 'RelaxNG', 'publiforge.rng')},
        'pack.xml' in zip_file.namelist() and zip_file.read('pack.xml') or '')
    if isinstance(pack_doc, basestring):
        request.session.flash(pack_doc, 'alert')
        zip_file.close()
        handler.close()
        return pack_doc

    # Check content
    error, pack_id, label, storage_ids = _pack_upload_content_check(
        request, project_id, pack_doc, label, zip_file)
    if error:
        zip_file.close()
        handler.close()
        return error

    # Check storage access, add and commit
    error = _pack_upload_content_extract(
        request, pack_doc, storage_ids, zip_file, message)
    zip_file.close()
    handler.close()
    if error:
        return error

    # Save settings
    DBSession.query(Pack).filter_by(label=label).delete()
    pack_upload_settings(request, project_id, pack_doc, pack_id)


# =============================================================================
def _pack_upload_content_check(request, project_id, pack_doc, label, zip_file):
    """Check pack content before importing it.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param project_id: (string)
        Current project ID.
    :param pack_doc: (:class:`lxml.etree.ElementTree` instance)
        Pack XML DOM.
    :param label: (string)
        Label of pack to replace. If ``None``, the pack must be a new one, if
        ``''``, the pack must exist.
    :param zip_file: (file handler)
        ZIP file handler.
    :return: (tuple)
        A tupple such as ``(error, pack_doc, pack_id, label, storage_ids)``.
    """
    # pylint: disable = locally-disabled, E1103
    # Error function
    def _error(error):
        """Return an error message."""
        request.session.flash(error, 'alert')
        return error, None, None, None

    # Check "pack.xml"
    item = normalize_spaces(pack_doc.findtext('pack/label'), LABEL_LEN)
    if label and label != item:
        return _error(_('Pack labels are different!'))
    pack = DBSession.query(Pack.pack_id).filter_by(
        project_id=project_id, label=item).first()
    if label is None and pack:
        return _error(_('Pack "${l}" already exists.', {'l': item}))
    if label == '' and pack is None:
        return _error(_('Pack "${l}" does not exist.', {'l': item}))
    label = item

    # Check ZIP content
    root = request.registry.settings['storage.root']
    storage_ids = set()
    for item in pack_doc.xpath(
            'pack/files/file|pack/resources/resource|pack/templates/template'):
        item = item.text.strip()
        if item not in EXCLUDED_FILES and item not in zip_file.namelist() \
                and not exists(join(root, item)):
            return _error(_('Unknown file "${n}".', {'n': item}))
        if item not in EXCLUDED_FILES and item in zip_file.namelist():
            item = item.split(sep)[0]
            if item not in storage_ids and not exists(join(root, item)):
                return _error(_('Unknown storage "${n}".', {'n': item}))
            storage_ids.add(item)

    return None, pack and pack[0] or None, label, storage_ids


# =============================================================================
def _pack_upload_content_extract(request, pack_doc, storage_ids, zip_file,
                                 message):
    """Check access to storage and extract files, add them and commit.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param pack_doc: (:class:`lxml.etree.ElementTree` instance)
        Pack XML DOM.
    :param storage_ids: (list)
        ZIP file handler.
    :param zip_file: (file handler)
        ZIP file handler.
    :param message: (string)
        Message for version control system.
    :return: (``None`` or :class:`pyramid.i18n.TranslationString`)
    """
    # Authorization for storages
    vcs_user = {}
    for storage_id in storage_ids:
        storage = DBSession.query(Storage).filter_by(storage_id=storage_id)\
            .first()
        if storage is None:
            return _('Unknown storage "${n}".', {'n': storage_id})
        user = DBSession.query(StorageUser).filter_by(
            storage_id=storage_id, user_id=request.session['user_id']).first()
        if not has_permission(request, 'stg_modifier') \
                and storage.access != 'open' \
                and (not user or not user.perm or user.perm == 'user'):
            return _('You cannot write into "${n}"!', {'n': storage_id})
        if storage.vcs_engine not in ('none', 'local') \
                and not (user and user.vcs_user):
            return _(
                'ID and password for "${n}" are missing.', {'n': storage_id})
        if storage.vcs_engine != 'none':
            vcs_user[storage_id] = (
                user and user.vcs_user or None,
                user and decrypt(
                    user.vcs_password,
                    request.registry.settings.get('encryption', '-')))
        request.registry['handler'].get_handler(storage_id, storage)

    # Extract content
    # pylint: disable = locally-disabled, E1103
    root = request.registry.settings['storage.root']
    for name in pack_doc.xpath(
            'pack/files/file|pack/resources/resource|pack/templates/template'):
        name = name.text.strip()
        if name in zip_file.namelist() \
                and basename(name) not in EXCLUDED_FILES:
            zip_file.extract(name, root)

    # Add and commit
    for storage_id in storage_ids:
        if storage_id in vcs_user:
            handler = request.registry['handler'].get_handler(storage_id)
            handler.add(
                (vcs_user[storage_id][0], vcs_user[storage_id][1],
                 request.session['name']), '.', message)
            name, error = handler.progress()
            if name == 'error':
                return error
            handler.cache.clear()
