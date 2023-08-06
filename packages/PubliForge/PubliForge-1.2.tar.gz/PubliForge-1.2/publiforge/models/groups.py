# $Id: groups.py e94a5cc5aef1 2014/08/19 07:57:32 Patrick $
"""SQLAlchemy-powered model definition for groups."""
# pylint: disable = locally-disabled, super-on-old-class

from lxml import etree
from sqlalchemy import Table, Column, ForeignKey, types
from sqlalchemy.orm import relationship

from ..lib.utils import _, normalize_name, normalize_spaces, make_id, wrap
from . import Base, DBSession, ID_LEN, LABEL_LEN, DESCRIPTION_LEN
from .users import PERM_SCOPES, USER_PERMS, User


GROUPS_USERS = Table(
    'groups_users', Base.metadata,
    Column(
        'group_id', types.String(ID_LEN),
        ForeignKey('groups.group_id', ondelete='CASCADE'), primary_key=True),
    Column(
        'user_id', types.Integer,
        ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True),
    mysql_engine='InnoDB')
XML_NS = '{http://www.w3.org/XML/1998/namespace}'


# =============================================================================
class Group(Base):
    """SQLAlchemy-powered group model."""

    __tablename__ = 'groups'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    group_id = Column(types.String(ID_LEN), primary_key=True)
    label = Column(types.String(LABEL_LEN), unique=True, nullable=False)
    description = Column(types.String(DESCRIPTION_LEN))
    perms = relationship('GroupPerm')
    users = relationship('User', secondary=GROUPS_USERS, backref='groups')

    # -------------------------------------------------------------------------
    def __init__(self, group_id, label, description=None):
        """Constructor method."""
        super(Group, self).__init__()
        self.group_id = make_id(group_id, 'token', ID_LEN)
        self.label = normalize_spaces(label, LABEL_LEN)
        self.description = normalize_spaces(description, DESCRIPTION_LEN)

    # -------------------------------------------------------------------------
    @classmethod
    def load(cls, group_elt, error_if_exists=True):
        """Load a group from a XML file.

        :param group_elt: (:class:`lxml.etree.Element` instance)
            Group XML element.
        :param error_if_exists: (boolean, default=True)
            It returns an error if group already exists.
        :return: (:class:`pyramid.i18n.TranslationString` or ``None``)
            Error message or ``None``.
        """
        # Check if already exists
        group_id = make_id(group_elt.get('%sid' % XML_NS), 'token', ID_LEN)
        label = normalize_spaces(group_elt.findtext('label'), LABEL_LEN)
        group = DBSession.query(cls).filter_by(group_id=group_id).first()
        if group is None:
            group = DBSession.query(cls).filter_by(label=label).first()
        if group is not None:
            if error_if_exists:
                return _('Group "${l} (${i})" already exists.',
                         {'i': group_id, 'l': label})
            return

        # Create group
        group = cls(group_id, label, group_elt.findtext('description'))
        DBSession.add(group)
        DBSession.commit()

        # Add permissions
        done = []
        for item in group_elt.findall('permissions/permission'):
            if item.get('scope') not in done:
                group.perms.append(GroupPerm(
                    group.group_id, item.get('scope'), item.text))
                done.append(item.get('scope'))

        # Add members
        done = []
        for item in group_elt.findall('members/member'):
            login = normalize_name(item.text)[0:ID_LEN]
            if login not in done:
                user = DBSession.query(User).filter_by(login=login).first()
                if user is not None:
                    group.users.append(user)
                done.append(login)

        DBSession.commit()

    # -------------------------------------------------------------------------
    def xml(self):
        """Serialize a group to a XML representation.

        :return: (:class:`lxml.etree.Element`)
        """
        group_elt = etree.Element('group')
        group_elt.set('%sid' % XML_NS, self.group_id)
        etree.SubElement(group_elt, 'label').text = self.label
        if self.description:
            etree.SubElement(group_elt, 'description').text = \
                wrap(self.description, indent=8)

        # Permissions
        if self.perms:
            elt = etree.SubElement(group_elt, 'permissions')
            for perm in self.perms:
                etree.SubElement(
                    elt, 'permission', scope=perm.scope).text = perm.level

        # Members
        if self.users:
            members_elt = etree.SubElement(group_elt, 'members')
            for user in self.users:
                user = DBSession.query(User.login).filter_by(
                    user_id=user.user_id).first()
                elt = etree.SubElement(members_elt, 'member').text = user[0]

        return group_elt


# =============================================================================
class GroupPerm(Base):
    """SQLAlchemy-powered group permission class."""
    # pylint: disable = locally-disabled, R0903, W0142

    __tablename__ = 'groups_perms'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    group_id = Column(
        types.String(ID_LEN),
        ForeignKey('groups.group_id', ondelete='CASCADE'), primary_key=True)
    scope = Column(
        types.Enum(*PERM_SCOPES.keys(), name='perm_scope_enum'),
        primary_key=True)
    level = Column(types.Enum(*USER_PERMS.keys(), name='grp_perms_enum'))

    # -------------------------------------------------------------------------
    def __init__(self, group_id, scope, level):
        """Constructor method."""
        super(GroupPerm, self).__init__()
        self.group_id = make_id(group_id, 'token', ID_LEN)
        self.scope = scope
        self.level = level
