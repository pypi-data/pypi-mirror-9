# $Id: users.py 7981fd623a54 2015/02/21 08:15:22 Patrick $
"""SQLAlchemy-powered model definition for users."""
# pylint: disable = locally-disabled, super-on-old-class

from datetime import datetime
from lxml import etree
from sqlalchemy import Column, ForeignKey, types
from sqlalchemy.orm import relationship

from ..lib.utils import _, hash_sha, normalize_name, normalize_spaces
from ..lib.utils import settings_get_list
from . import ID_LEN, LABEL_LEN, Base, DBSession


USER_STATUS = {'active': _('active'), 'inactive': _('inactive')}
PERM_SCOPES = {
    'all': _('All'), 'doc': _('Documentation'), 'usr': _('Users'),
    'grp': _('Groups'), 'stg': _('Storages'), 'idx': _('Indexing'),
    'prj': _('Projects')}
USER_PERMS = {
    'manager': _('Manager'), 'editor': _('Editor'), 'user': _('User')}
HOMES = {
    'site': _('Site administration'), 'projects': _('Project list'),
    'storages': _('Storage list')}
PAGE_SIZE = 20


# =============================================================================
class User(Base):
    """SQLAlchemy-powered user model."""
    # pylint: disable = locally-disabled, star-args
    # pylint: disable = locally-disabled, too-many-instance-attributes

    __tablename__ = 'users'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    user_id = Column(types.Integer, primary_key=True)
    login = Column(types.String(ID_LEN), unique=True, nullable=False)
    status = Column(
        types.Enum(*USER_STATUS.keys(), name='usr_status_enum'),
        nullable=False)
    password = Column(types.String(64))
    name = Column(types.String(LABEL_LEN), nullable=False)
    email = Column(types.String(LABEL_LEN), nullable=False)
    lang = Column(types.String(5), nullable=False)
    expiration = Column(types.Date)
    restrict_ip = Column(types.Boolean, default=False)
    home = Column(
        types.Enum(*HOMES.keys(), name='usr_home_enum'), default='projects',
        nullable=False)
    page_size = Column(types.Integer, default=PAGE_SIZE)
    last_login = Column(types.DateTime)
    updated = Column(types.DateTime)
    created = Column(types.DateTime, default=datetime.now)
    perms = relationship('UserPerm')
    ips = relationship('UserIP')

    # -------------------------------------------------------------------------
    def __init__(self, settings, login, status, password, name, email,
                 lang='en', expiration=None, restrict_ip=False, home=None,
                 page_size=None, created=None, updated=None):
        """Constructor method."""
        # pylint: disable = locally-disabled, too-many-arguments
        super(User, self).__init__()
        self.login = normalize_name(login)[0:ID_LEN]
        self.status = status
        self.set_password(settings, password)
        self.name = normalize_spaces(name, LABEL_LEN)
        self.email = email[0:LABEL_LEN]
        self.lang = lang[0:5]
        self.expiration = isinstance(expiration, basestring) \
            and datetime.strptime(expiration, '%Y-%m-%d') or expiration
        self.restrict_ip = restrict_ip
        self.home = home
        self.page_size = page_size
        self.created = created is None and datetime.now() \
            or datetime.strptime(created, '%Y-%m-%dT%H:%M:%S')
        if updated is not None:
            self.updated = datetime.strptime(updated, '%Y-%m-%dT%H:%M:%S')

    # -------------------------------------------------------------------------
    def set_password(self, settings, password):
        """Encrypt and set password.

        :param settings: (dictionary)
            Pyramid deployment settings.
        :param password: (string)
            Clear password.
        """
        if password:
            self.password = hash_sha(
                password.strip(), settings.get('encryption', '-'))

    # -------------------------------------------------------------------------
    def setup_environment(self, request):
        """Set up user environment (session and cookie).

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.

        It saves in session the following values:

        * ``user_id``: user ID
        * ``name``: user name
        * ``page_size``: items per page in listsg
        * ``home``: home page content
        """
        # pylint: disable = locally-disabled, E1101
        # User information
        request.session.clear()
        request.session['user_id'] = self.user_id
        request.session['login'] = self.login
        request.session['name'] = self.name
        request.session['home'] = self.home
        request.session['paging'] = (self.page_size, {})

        # Language
        langs = settings_get_list(request.registry.settings, 'languages')
        request.session['lang'] = (self.lang in langs and self.lang) \
            or (self.lang[0:2] in langs and self.lang[0:2]) \
            or request.registry.settings.get('pyramid.default_locale_name')

        # Permissions
        perms = {}
        levels = {'user': 1, 'editor': 2, 'manager': 3, 'admin': 4}
        for perm in self.perms:
            perms[perm.scope] = perm.level
        for group in self.groups:
            for perm in group.perms:
                if perm.scope not in perms or \
                        levels[perms[perm.scope]] < levels[perm.level]:
                    perms[perm.scope] = perm.level
        if 'all' in perms and perms['all'] != 'admin':
            perm = levels[perms['all']]
            for scope in PERM_SCOPES.keys()[1:]:
                if scope not in perms or levels[perms[scope]] < perm:
                    perms[scope] = perms['all']
            del perms['all']
        request.session['perms'] = perms.get('all') == 'admin' and ('admin',) \
            or tuple(['%s_%s' % (k, perms[k]) for k in perms])

    # -------------------------------------------------------------------------
    @classmethod
    def load(cls, settings, user_elt, error_if_exists=True):
        """Load a user from a XML file.

        :param settings: (dictionary)
            Application settings.
        :param user_elt: (:class:`lxml.etree.Element` instance)
            User XML element.
        :param error_if_exists: (boolean, default=True)
            It returns an error if user already exists.
        :return: (:class:`pyramid.i18n.TranslationString` or ``None``)
            Error message or ``None``.
        """
        # Check if already exists
        login = normalize_name(user_elt.get('login'))[0:ID_LEN]
        user = DBSession.query(cls).filter_by(login=login).first()
        if user is not None:
            if error_if_exists:
                return _('User "${l}" already exists.', {'l': login})
            return

        # Create user
        # pylint: disable = locally-disabled, W0142
        record = {
            'status':
            user_elt.get('status', 'active'),
            'created':
            user_elt.get('created'),
            'updated':
            user_elt.get('updated'),
            'password':
            user_elt.findtext('password') is not None and
            user_elt.findtext('password').strip() or None,
            'name':
            user_elt.findtext('name'),
            'email':
            user_elt.findtext('email').strip(),
            'lang':
            user_elt.findtext('language') is not None and
            user_elt.findtext('language') or
            settings['pyramid.default_locale_name'],
            'expiration':
            user_elt.findtext('expiration') is not None and
            user_elt.findtext('expiration') or None,
            'restrict_ip':
            bool(user_elt.find('ips') is not None),
            'home':
            user_elt.findtext('home') is not None and
            user_elt.findtext('home').strip() or None,
            'page_size':
            user_elt.findtext('page_size') is not None and
            int(user_elt.findtext('page_size').strip()) or None}
        user = cls(settings, login, **record)
        if record['password'] and user_elt.find('password').get('hash'):
            user.password = record['password']
        DBSession.add(user)
        DBSession.commit()

        # Add permissions
        done = []
        for item in user_elt.findall('permissions/permission'):
            if item.get('scope') not in done:
                user.perms.append(
                    UserPerm(user.user_id, item.get('scope'), item.text))
                done.append(item.get('scope'))

        # Add IP restriction
        done = []
        for item in user_elt.findall('ips/ip'):
            if item.text not in done:
                user.ips.append(UserIP(user.user_id, item.text))
                done.append(item.text)

        DBSession.commit()

    # -------------------------------------------------------------------------
    def xml(self, i_manager=False):
        """Serialize a user to a XML representation.

        :param i_manager: (boolean, default=False)
            Am I a user manager?
        :return: (:class:`lxml.etree.Element`)
        """
        if 'admin' in [k.level for k in self.perms]:
            return

        user_elt = etree.Element('user')
        user_elt.set('login', self.login)
        user_elt.set('created', self.created.isoformat().partition('.')[0])
        if self.updated and self.created != self.updated:
            user_elt.set('updated', self.updated.isoformat().partition('.')[0])
        etree.SubElement(user_elt, 'name').text = self.name
        if i_manager:
            etree.SubElement(
                user_elt, 'password', hash='true').text = self.password
        etree.SubElement(user_elt, 'email').text = self.email
        etree.SubElement(user_elt, 'language').text = self.lang
        etree.SubElement(user_elt, 'home').text = self.home
        if self.page_size != PAGE_SIZE:
            etree.SubElement(user_elt, 'page_size').text = str(self.page_size)
        if self.expiration:
            etree.SubElement(user_elt, 'expiration').text = \
                self.expiration.isoformat()

        # Permissions
        if self.perms:
            elt = etree.SubElement(user_elt, 'permissions')
            for perm in self.perms:
                etree.SubElement(
                    elt, 'permission', scope=perm.scope).text = perm.level

        # IPs
        if self.ips:
            elt = etree.SubElement(user_elt, 'ips')
            for item in self.ips:
                etree.SubElement(elt, 'ip').text = item.ip

        return user_elt


# =============================================================================
class UserPerm(Base):
    """SQLAlchemy-powered user permission class."""
    # pylint: disable = locally-disabled, R0903, W0142

    __tablename__ = 'users_perms'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    user_id = Column(
        types.Integer,
        ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    scope = Column(
        types.Enum(*PERM_SCOPES.keys(), name='perm_scope_enum'),
        primary_key=True)
    level = Column(
        types.Enum(*(['admin'] + USER_PERMS.keys()), name='usr_perms_enum'))

    # -------------------------------------------------------------------------
    def __init__(self, user_id, scope, level):
        """Constructor method."""
        super(UserPerm, self).__init__()
        self.user_id = user_id
        self.scope = level == 'admin' and 'all' or scope
        self.level = level


# =============================================================================
class UserIP(Base):
    """Class for restriction by IP."""
    # pylint: disable = locally-disabled, C0103, R0903

    __tablename__ = 'users_ips'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    user_id = Column(
        types.Integer,
        ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    ip = Column(types.String(40), primary_key=True)

    # -------------------------------------------------------------------------
    def __init__(self, user_id, ip):
        """Constructor method."""
        super(UserIP, self).__init__()
        self.user_id = user_id
        self.ip = ip
