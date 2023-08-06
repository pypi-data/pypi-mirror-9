#!/usr/bin/env python
# $Id: pfpopulate.py d394b2d7e0a4 2014/11/27 16:54:42 Patrick $
"""Populate database and storages."""

import logging
from argparse import ArgumentParser
from os import listdir, getcwd
from os.path import exists, join, basename, normpath
from ConfigParser import ConfigParser
from locale import getdefaultlocale
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from sqlalchemy import engine_from_config
from sqlalchemy.exc import OperationalError

from pyramid.paster import get_appsettings

from ..lib.utils import _, localizer, config_get, settings_get_list
from ..lib.utils import normalize_name
from ..lib.xml import import_configuration
from ..lib.handler import HandlerManager
from ..models import ID_LEN, DBSession, Base
from ..models.users import PAGE_SIZE, User, UserPerm, UserIP
from ..models.storages import Storage


__credits__ = '(c) Prismallia http://www.prismallia.fr, 2014'


LOG = logging.getLogger(__name__)


# =============================================================================
def main():
    """Main function."""
    # Parse arguments
    parser = ArgumentParser(description='Populate database and storages.')
    parser.add_argument(
        'conf_uri', help='URI of configuration (e.g. production.ini#foo)')
    parser.add_argument(
        'files', nargs='*', help='optional XML configuration files to use')
    parser.add_argument(
        '--drop-tables', dest='drop_tables', help='drop existing tables',
        action='store_true')
    parser.add_argument(
        '--no-pull', dest='no_pull', help='do not synchronize storages',
        action='store_true')
    parser.add_argument(
        '--reset-index', dest='reset_index', help='delete storage indexes',
        action='store_true')
    parser.add_argument(
        '--no-index', dest='no_index', help='do not index storages',
        action='store_true')
    parser.add_argument(
        '--log-level', dest='log_level', help='log level', default='INFO',
        choices=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'))
    args = parser.parse_args()
    if not exists(args.conf_uri.partition('#')[0]):
        parser.print_usage()
        return

    # Initialize log
    logformat = '%(asctime)s %(levelname)-8s %(message)s'
    logging.basicConfig(level=args.log_level, format=logformat)

    # Populate database and storage
    Populate(args, args.conf_uri).all(args.files)


# =============================================================================
class Populate(object):
    """Class to populate database and storages."""

    # -------------------------------------------------------------------------
    def __init__(self, args, conf_uri):
        """Constructor method."""
        self._args = args
        self._settings = get_appsettings(conf_uri)
        if len(self._settings) < 3:
            try:
                self._settings = get_appsettings(conf_uri, 'PubliForge')
            except LookupError:
                self._settings = get_appsettings(conf_uri, basename(getcwd()))
        self._config = ConfigParser({'here': self._settings['here']})
        self._config.read(self._settings['__file__'])
        self._lang = self._settings.get('pyramid.default_locale_name')

    # -------------------------------------------------------------------------
    def all(self, files=tuple()):
        """Check settings, initialize database and create storages.

        :param files: (list, optional)
             List of files on command-line.
        :return: (boolean)
        """
        # Check general settings
        if not self._lang \
                or not settings_get_list(self._settings, 'languages'):
            LOG.error(self._translate(_(
                'Must define available languages and a default one.')))
            return False
        if not self._settings.get('uid'):
            LOG.error(self._translate(_(
                'Must define an unique identifier for this instance.')))
            return False

        # Agent only
        if self._settings.get('storage.root') is None:
            return True

        # Populate
        if not self._initialize_sql():
            return False
        self._populate_admin()
        self._populate_from_xml(files)
        if DBSession.query(UserPerm)\
                .filter_by(scope='all', level='admin').first() is None:
            LOG.error(self._translate(_('You must define an administrator.')))
            DBSession.remove()
            return False
        self._update_storages()
        DBSession.remove()
        return True

    # -------------------------------------------------------------------------
    def _initialize_sql(self):
        """Database initialization.

        :return: (boolean)
            ``True`` if it succeeds.
        """
        # Initialize SqlAlchemy session
        dbengine = engine_from_config(self._settings, 'sqlalchemy.')
        DBSession.configure(bind=dbengine)
        Base.metadata.bind = dbengine

        # Eventually, drop any existing tables
        if self._args.drop_tables or bool(self._settings.get('drop_tables')):
            LOG.info(self._translate(_('###### Dropping existing tables')))
            try:
                Base.metadata.drop_all()
            except OperationalError as error:
                LOG.error(error.args[0])
                return False

        # Create the tables if they don't already exist
        try:
            Base.metadata.create_all(dbengine)
        except OperationalError as error:
            LOG.error(error.args[0])
            return False

        return True

    # -------------------------------------------------------------------------
    def _populate_admin(self):
        """Populate database with an administrator."""
        # pylint: disable = locally-disabled, W0142
        if not self._config.has_option('Populate', 'admin.login'):
            return

        LOG.info(self._translate(_('###### Adding administrator')))
        login = normalize_name(self._get('admin.login'))[0:ID_LEN]
        ips = self._get('admin.ips', '')
        record = {
            'status': 'active',
            'password': self._get('admin.password'),
            'name': self._get('admin.name'),
            'email': self._get('admin.email'),
            'lang': self._get('admin.language', self._lang),
            'restrict_ip': bool(ips),
            'home': self._get('admin.home', 'site'),
            'page_size': int(self._get('admin.page_size', PAGE_SIZE))}
        if not record['password'] or not record['name']\
                or not record['email']:
            exit('*** Incorrect administrator definition.')
        user = DBSession.query(User.login).filter_by(login=login).first()
        if user is not None:
            return
        user = User(self._settings, login, **record)
        DBSession.add(user)
        DBSession.commit()

        user.perms.append(UserPerm(user.user_id, 'all', 'admin'))
        for my_ip in ips.split():
            user.ips.append(UserIP(user.user_id, my_ip))
        DBSession.commit()

    # -------------------------------------------------------------------------
    def _populate_from_xml(self, files):
        """Populate database with XML content.

        :param files: (list)
             List of files on command-line.
        """
        if not self._config.has_section('Populate') and not files:
            return
        LOG.info(self._translate(_('###### Loading configurations')))
        for idx in range(100):
            option = 'file.%d' % idx
            if not self._config.has_option('Populate', option):
                continue
            filename = normpath(self._get(option))
            LOG.info(filename)
            errors = import_configuration(
                self._settings, filename, error_if_exists=False)
            for error in errors:
                LOG.error(self._translate(error))

        for filename in files:
            LOG.info(filename)
            errors = import_configuration(
                self._settings, filename, error_if_exists=False)
            for error in errors:
                LOG.error(self._translate(error))

    # -------------------------------------------------------------------------
    def _update_storages(self):
        """Update all storages."""
        # pylint: disable = locally-disabled, logging-format-interpolation
        cache_manager = CacheManager(
            **parse_cache_config_options(self._settings))
        handler_manager = HandlerManager(self._settings, cache_manager)

        if self._args.reset_index and 'storage.index' in self._settings \
                and exists(self._settings['storage.index']):
            LOG.info(self._translate(_('###### Reseting indexes')))
            handler_manager.delete_index(False)

        LOG.info(self._translate(_('###### Updating storages')))
        for storage in DBSession.query(Storage):
            storage_dir = join(
                self._settings['storage.root'], storage.storage_id)
            handler = handler_manager.get_handler(storage.storage_id, storage)
            if handler is None:
                LOG.error(self._translate(
                    _('${e}: unkwown engine', {'e': storage.vcs_engine})))
            elif not exists(storage_dir) or not listdir(storage_dir):
                LOG.info('{0:.<32}'.format(storage.storage_id))
                error = handler.clone()
                if error:
                    LOG.error(error)
                elif not self._args.no_index:
                    handler_manager.index(storage.storage_id)
            elif not hasattr(self._args, 'no_pull') \
                    or not self._args.no_pull:
                LOG.info('{0:.<32}'.format(storage.storage_id))
                handler.synchronize(None, True)
                if not self._args.no_index:
                    handler_manager.index(storage.storage_id)

    # -------------------------------------------------------------------------
    def _get(self, option, default=None):
        """Retrieve a value from section [Populate].

        :param option: (string)
            Option name.
        :param default: (string, optional)
            Default value
        :return: (string)
            Read value or default value.
        """
        return config_get(self._config, 'Populate', option, default)

    # -------------------------------------------------------------------------
    @classmethod
    def _translate(cls, text):
        """Return ``text`` translated.

        :param text: (string)
            Text to translate.
        """
        return localizer(getdefaultlocale()[0]).translate(text)


# =============================================================================
if __name__ == '__main__':
    main()
