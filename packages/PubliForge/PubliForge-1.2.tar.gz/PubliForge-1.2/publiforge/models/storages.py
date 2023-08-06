# $Id: storages.py 7981fd623a54 2015/02/21 08:15:22 Patrick $
# -*- coding: utf-8 -*-
"""SQLAlchemy-powered model definition for storages."""
# pylint: disable = locally-disabled, super-on-old-class

from os.path import exists, join
import shutil
from lxml import etree
from sqlalchemy import Column, ForeignKey, types
from sqlalchemy.orm import relationship

from ..lib.utils import _, encrypt, normalize_name, normalize_spaces, wrap
from . import ID_LEN, LABEL_LEN, DESCRIPTION_LEN, PATH_LEN, PATTERN_LEN
from . import Base, DBSession
from .users import User
from .groups import Group


STORAGE_ACCESS = {
    'open': _('open'), 'restricted': _('restricted'), 'closed': _('closed')}
VCS_ENGINES = {
    'none': _(u'none – None'), 'local': _(u'local – Local'),
    'hg': u'hg – Mercurial', 'hgsvn': u'hgsvn – Subversion (hg)',
    'svn': u'svn – Subversion'}
STORAGE_PERMS = {'writer': _('File editor'), 'reader': _('File reader')}
REFRESH = 3600


# =============================================================================
class Storage(Base):
    """SQLAlchemy-powered storage model."""
    # pylint: disable = locally-disabled, star-args
    # pylint: disable = locally-disabled, too-many-instance-attributes

    __tablename__ = 'storages'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    storage_id = Column(types.String(ID_LEN), primary_key=True)
    label = Column(types.String(LABEL_LEN), unique=True, nullable=False)
    description = Column(types.String(DESCRIPTION_LEN))
    vcs_engine = Column(
        types.Enum(*VCS_ENGINES.keys(), name='vcs_engine_enum'),
        nullable=False)
    vcs_url = Column(types.String(PATH_LEN))
    vcs_user = Column(types.String(ID_LEN))
    vcs_password = Column(types.String(64))
    public_url = Column(types.String(PATH_LEN))
    access = Column(
        types.Enum(*STORAGE_ACCESS.keys(), name='stg_access_enum'),
        nullable=False, default='open')
    refresh = Column(types.Integer, default=REFRESH)
    indexed_files = Column(types.String(PATTERN_LEN))
    openers = relationship('StorageOpener')
    users = relationship('StorageUser', backref='storage')
    groups = relationship('StorageGroup')

    # -------------------------------------------------------------------------
    def __init__(self, settings, storage_id, label, description=None,
                 vcs_engine='local', vcs_url=None, vcs_user=None,
                 vcs_password=None, public_url=None, access=None,
                 refresh=None, indexed_files=None):
        """Constructor method."""
        # pylint: disable = locally-disabled, too-many-arguments
        super(Storage, self).__init__()
        self.storage_id = storage_id.strip()[0:ID_LEN]
        self.label = normalize_spaces(label, LABEL_LEN)
        self.description = normalize_spaces(description, DESCRIPTION_LEN)
        self.access = access
        self.vcs_engine = vcs_engine
        if vcs_engine not in ('none', 'local'):
            self.vcs_url = vcs_url[0:PATH_LEN]
            self.vcs_user = vcs_user and vcs_user.strip()[0:ID_LEN]
            self.set_vcs_password(settings, vcs_password)
        elif public_url is not None:
            self.public_url = public_url.strip()[0:PATH_LEN]
        self.refresh = refresh
        self.indexed_files = indexed_files and indexed_files.strip() or None

    # -------------------------------------------------------------------------
    def set_vcs_password(self, settings, vcs_password):
        """Encrypt and set password.

        :param settings: (dictionary)
            Pyramid deployment settings.
        :param vcs_password: (string)
            Clear VCS password.
        """
        if vcs_password:
            self.vcs_password = encrypt(
                vcs_password.strip(), settings.get('encryption', '-'))

    # -------------------------------------------------------------------------
    @classmethod
    def delete(cls, storage_root, storage_id):
        """Delete a storage.

        :param storage_root: (string)
            Storage root path.
        :param storage_id: (string)
            Storage identifier.
        """
        # Delete records in database
        DBSession.query(cls).filter_by(storage_id=storage_id).delete()
        DBSession.commit()

        # Remove directory
        if exists(join(storage_root, storage_id)):
            shutil.rmtree(join(storage_root, storage_id))

    # -------------------------------------------------------------------------
    @classmethod
    def load(cls, settings, storage_elt, error_if_exists=True):
        """Load a storage from a XML file.

        :param settings: (dictionary)
            Application settings.
        :param storage_elt: (:class:`lxml.etree.Element` instance)
            Storage XML element.
        :param error_if_exists: (boolean, default=True)
            It returns an error if storage already exists.
        :return: (:class:`pyramid.i18n.TranslationString` ``None`` or
            :class:`Storage` instance)
            Error message or ``None`` or the new storage object.
        """
        # Reset
        storage_id = storage_elt.get('id').strip()[0:ID_LEN]
        label = normalize_spaces(storage_elt.findtext('label'), LABEL_LEN)
        if storage_elt.find('reset') is not None \
                and bool(storage_elt.findtext('reset')):
            Storage.delete(settings['storage.root'], storage_id)

        # Check if already exists
        storage = DBSession.query(cls).filter_by(
            storage_id=storage_id).first()
        if storage is None:
            storage = DBSession.query(cls).filter_by(label=label).first()
        if storage is not None:
            if error_if_exists:
                return _(
                    'Storage "${i}" already exists.', {'i': storage_id})
            return

        # Create storage
        # pylint: disable = locally-disabled, W0142
        vcs_elt = storage_elt.find('vcs')
        record = {
            'label': label,
            'description':
            storage_elt.findtext('description'),
            'vcs_engine':
            vcs_elt.get('engine'),
            'vcs_url':
            vcs_elt.findtext('url') is not None and
            vcs_elt.findtext('url').strip() or None,
            'vcs_user':
            vcs_elt.findtext('user') is not None and
            vcs_elt.findtext('user').strip() or None,
            'vcs_password':
            vcs_elt.findtext('password') is not None and
            vcs_elt.findtext('password').strip() or None,
            'public_url':
            vcs_elt.findtext('public') is not None and
            vcs_elt.findtext('public').strip() or None,
            'access':
            storage_elt.findtext('access') is not None and
            storage_elt.findtext('access').strip() or 'open',
            'refresh':
            storage_elt.findtext('refresh') is not None and
            int(storage_elt.findtext('refresh').strip()) or None,
            'indexed_files':
            storage_elt.findtext('indexed') is not None and
            storage_elt.findtext('indexed') or None}
        storage = Storage(settings, storage_id, **record)
        if record['vcs_password'] and vcs_elt.find('password').get('encrypt'):
            storage.vcs_password = record['vcs_password']
        DBSession.add(storage)
        DBSession.commit()

        # Load additional element
        return cls._load_additional(storage_elt, storage)

    # -------------------------------------------------------------------------
    @classmethod
    def _load_additional(cls, storage_elt, storage):
        """Load additional elements as openers, users and groups.

        :param storage_elt: (:class:`lxml.etree.Element` instance)
            Current storage DOM element.
        :param storage: (:class:`Storage`)
            Current storage record
        :return: (:class:`Storage` instance)
            The new storage object.
        """
        # Add openers
        done = set()
        for item in storage_elt.findall('openers/opener'):
            opener_id = item.text[0:ID_LEN]
            if opener_id not in done:
                storage.openers.append(
                    StorageOpener(
                        storage.storage_id, opener_id, len(done) + 1))
                done.add(opener_id)

        # Add users
        done = set()
        for item in storage_elt.findall('members/member'):
            login = normalize_name(item.text)[0:ID_LEN]
            if login not in done:
                user = DBSession.query(User).filter_by(login=login).first()
                if user is not None:
                    storage.users.append(StorageUser(
                        storage.storage_id, user.user_id,
                        item.get('in-menu'), item.get('permission', 'reader'),
                        vcs_user=item.get('vcs-user'),
                        vcs_password=item.get('vcs-password')))
                done.add(login)

        # Add groups
        done = set()
        for item in storage_elt.findall('members/member-group'):
            group_id = normalize_name(item.text)[0:ID_LEN]
            if group_id not in done:
                group = DBSession.query(Group).filter_by(
                    group_id=group_id).first()
                if group is not None:
                    storage.groups.append(
                        StorageGroup(
                            storage.storage_id, group.group_id,
                            item.get('permission')))
                done.add(group_id)

        DBSession.commit()
        return storage

    # -------------------------------------------------------------------------
    def xml(self):
        """Serialize a storage to a XML representation.

        :return: (:class:`lxml.etree.Element`)
        """
        # pylint: disable = locally-disabled, R0912
        storage_elt = etree.Element('storage')
        storage_elt.set('id', self.storage_id)
        etree.SubElement(storage_elt, 'label').text = self.label
        if self.description:
            etree.SubElement(storage_elt, 'description').text = \
                wrap(self.description, indent=8)
        elt = etree.SubElement(storage_elt, 'vcs')
        elt.set('engine', self.vcs_engine)
        if self.vcs_url:
            etree.SubElement(elt, 'url').text = self.vcs_url
        if self.vcs_user:
            etree.SubElement(elt, 'user').text = self.vcs_user
            etree.SubElement(elt, 'password', encrypt='true').text = \
                self.vcs_password
        if self.public_url:
            etree.SubElement(elt, 'public').text = self.public_url
        if self.access != 'open':
            etree.SubElement(storage_elt, 'access').text = self.access
        if self.refresh != REFRESH:
            etree.SubElement(storage_elt, 'refresh').text = str(self.refresh)
        if self.indexed_files:
            etree.SubElement(storage_elt, 'indexed').text = self.indexed_files

        # Openers
        if self.openers:
            openers_elt = etree.SubElement(storage_elt, 'openers')
            for opener in sorted(self.openers, key=lambda k: k.sort):
                elt = etree.SubElement(openers_elt, 'opener')
                elt.text = opener.opener_id

        # Members
        if self.users or self.groups:
            members_elt = etree.SubElement(storage_elt, 'members')
            for user in self.users:
                elt = etree.SubElement(members_elt, 'member')
                elt.text = user.user.login
                if user.in_menu:
                    elt.set('in-menu', 'true')
                if user.perm != 'reader':
                    elt.set('permission', user.perm or 'none')
                if user.vcs_user:
                    elt.set('vcs-user', user.vcs_user)
                    if user.vcs_password:
                        elt.set('vcs-password', user.vcs_password)
            for group in self.groups:
                elt = etree.SubElement(members_elt, 'member-group')
                elt.text = group.group_id
                if group.perm != 'reader':
                    elt.set('permission', group.perm)

        return storage_elt


# =============================================================================
class StorageOpener(Base):
    """SQLAlchemy-powered association table between ``Storage`` and its
    openers."""
    # pylint: disable = locally-disabled, too-few-public-methods
    __tablename__ = 'storages_openers'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    storage_id = Column(
        types.String(ID_LEN),
        ForeignKey('storages.storage_id', ondelete='CASCADE'),
        primary_key=True)
    opener_id = Column(types.String(ID_LEN), primary_key=True)
    sort = Column(types.Integer, default=0)

    # -------------------------------------------------------------------------
    def __init__(self, storage_id, opener_id, sort=0):
        """Constructor method."""
        super(StorageOpener, self).__init__()
        self.storage_id = storage_id.strip()[0:ID_LEN]
        self.opener_id = opener_id.strip()[0:ID_LEN]
        self.sort = sort


# =============================================================================
class StorageUser(Base):
    """SQLAlchemy-powered association table between ``Storage`` and
    ``User``."""
    # pylint: disable = locally-disabled, R0913, W0142

    __tablename__ = 'storages_users'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    storage_id = Column(
        types.String(ID_LEN),
        ForeignKey('storages.storage_id', ondelete='CASCADE'),
        primary_key=True)
    user_id = Column(
        types.Integer, ForeignKey('users.user_id', ondelete='CASCADE'),
        primary_key=True)
    in_menu = Column(types.Boolean, default=False)
    perm = Column(types.Enum(*STORAGE_PERMS.keys(), name='stg_perms_enum'))
    vcs_user = Column(types.String(ID_LEN))
    vcs_password = Column(types.String(40))
    user = relationship('User')

    # -------------------------------------------------------------------------
    def __init__(self, storage_id, user_id, in_menu=False, perm='reader',
                 vcs_user=None, vcs_password=None, settings=None):
        """Constructor method."""
        super(StorageUser, self).__init__()
        self.storage_id = storage_id.strip()[0:ID_LEN]
        self.user_id = user_id
        self.in_menu = bool(in_menu)
        if perm != 'none':
            self.perm = perm
        self.vcs_user = vcs_user
        self.vcs_password = vcs_password
        if vcs_password and settings is not None:
            self.set_vcs_password(settings, vcs_password)

    # -------------------------------------------------------------------------
    def set_vcs_password(self, settings, vcs_password):
        """Encrypt and set VCS password.

        :param settings: (dictionary)
            Pyramid deployment settings.
        :param password: (string)
            Clear password.
        """
        self.vcs_password = encrypt(
            vcs_password, settings.get('encryption', '-'))


# =============================================================================
class StorageGroup(Base):
    """SQLAlchemy-powered association table between ``Storage`` and
    ``Group``."""
    # pylint: disable = locally-disabled, W0142, R0903

    __tablename__ = 'storages_groups'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    storage_id = Column(
        types.String(ID_LEN),
        ForeignKey('storages.storage_id', ondelete='CASCADE'),
        primary_key=True)
    group_id = Column(
        types.String(ID_LEN),
        ForeignKey('groups.group_id', ondelete='CASCADE'), primary_key=True)
    perm = Column(
        types.Enum(*STORAGE_PERMS.keys(), name='stg_perms_enum'),
        default='reader')

    # -------------------------------------------------------------------------
    def __init__(self, storage_id, group_id, perm=None):
        """Constructor method."""
        super(StorageGroup, self).__init__()
        self.storage_id = storage_id.strip()[0:ID_LEN]
        self.group_id = group_id.strip()[0:ID_LEN]
        self.perm = perm
