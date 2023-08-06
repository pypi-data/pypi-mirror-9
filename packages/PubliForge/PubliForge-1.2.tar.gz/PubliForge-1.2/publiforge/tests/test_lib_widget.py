# $Id: test_lib_widget.py 423387b2062e 2014/07/27 21:39:58 Patrick $
# pylint: disable = locally-disabled, R0904
"""Tests of ``lib.widget`` classes and functions."""

import unittest

from pyramid import testing

from ..tests import ModelTestCase


# =============================================================================
class UnitTestLibWidgetHasPermission(unittest.TestCase):
    """Unit test class for ``lib.widget.has_permission``."""

    # -------------------------------------------------------------------------
    def test_unauthenticated(self):
        """[u:lib.widget.has_permission] unauthenticated"""
        from ..lib.widget import has_permission
        request = testing.DummyRequest()
        self.assertFalse(has_permission(request, 'usr_user'))

    # -------------------------------------------------------------------------
    def test_with_admin(self):
        """[u:lib.widget.has_permission] with administrator"""
        from ..lib.widget import has_permission
        request = testing.DummyRequest()
        request.session['perms'] = ('admin',)
        self.assertTrue(has_permission(request, 'usr_manager'))

    # -------------------------------------------------------------------------
    def test_with_user(self):
        """[u:lib.widget.has_permission] with normal user"""
        from ..lib.widget import has_permission
        request = testing.DummyRequest()
        request.session['perms'] = ('usr_manager', 'grp_editor')
        self.assertTrue(has_permission(request, 'usr_user'))
        self.assertTrue(has_permission(request, 'usr_editor'))
        self.assertTrue(has_permission(request, 'usr_manager'))
        self.assertTrue(has_permission(request, 'grp_user'))
        self.assertTrue(has_permission(request, 'grp_editor'))
        self.assertFalse(has_permission(request, 'grp_manager'))
        self.assertFalse(has_permission(request, 'stg_user'))
        self.assertFalse(has_permission(request, 'stg_editor'))
        self.assertFalse(has_permission(request, 'stg_manager'))


# =============================================================================
class UnitTestLibWidgetMenu(ModelTestCase):
    """Unit test class for ``lib.widget.Menu``."""
    # pylint: disable = locally-disabled, C0103, R0904, W0212

    _key = 'seekrit'
    _user_id = 1000
    _storage_id = '_test_storage'
    _project_id = 1000

    # -------------------------------------------------------------------------
    def tearDown(self):
        """Undo the effects ``pyramid.testing.setUp()``."""
        from ..models.users import User
        from ..models.projects import Project
        from ..models.storages import Storage
        self.session.query(User).filter_by(user_id=self._user_id).delete()
        if self.session.query(Storage)\
               .filter_by(storage_id=self._storage_id).first() is not None:
            Storage.delete('/tmp', self._storage_id)
        self.session.query(Project)\
            .filter_by(project_id=self._project_id).delete()
        self.session.commit()
        ModelTestCase.tearDown(self)

    # -------------------------------------------------------------------------
    def _make_one(self):
        """Make a ``Menu`` object."""
        from ..lib.widget import Menu
        from ..models.users import User
        from ..models.storages import Storage, StorageUser
        from ..models.projects import Project, ProjectUser
        # User, storage and project
        user = User({'encryption': self._key}, '_test_user', status='active',
                    password='pass', name=u'Marc', email='test@prismallia.fr',
                    lang='en')
        user.user_id = self._user_id
        self.session.add(user)
        storage = Storage(
            {'encryption': self._key}, self._storage_id, 'open', 'local')
        storage.users.append(StorageUser(
            self._storage_id, user.user_id, True))
        self.session.add(storage)
        project = Project(u'My project', 'active')
        project.project_id = self._project_id
        project.users.append(ProjectUser(
            project.project_id, self._user_id, True))
        self.session.add(project)
        self.session.commit()
        # Routes
        self.config.add_route('user_admin', '/user/admin')
        self.config.add_route('group_admin', '/group/admin')
        self.config.add_route('storage_admin', '/storage/admin')
        self.config.add_route('storage_index', '/storage/index')
        self.config.add_route('storage_root',
                              '/storage/browse/{storage_id}')
        self.config.add_route('storage_browse',
                              '/storage/browse/{storage_id}/*path')
        self.config.add_route('file_search', '/file/search')
        self.config.add_route('project_admin', '/project/admin')
        self.config.add_route('project_index', '/project/index')
        self.config.add_route('project_view', '/project/view/{project_id}')
        self.config.add_route('project_dashboard',
                              '/project/dashboard/{project_id}')
        self.config.add_route('task_index', '/task/index/{project_id}')
        self.config.add_route('pack_index', '/pack/index/{project_id}')
        self.config.add_route('build_results', '/build/results/{project_id}')

        # Dummy request
        request = testing.DummyRequest()
        request.session['perms'] = (
            'stg_user', 'prj_user', 'usr_manager', 'grp_editor')
        request.session['lang'] = 'fr'
        request.session['user_id'] = self._user_id
        request.session['breadcrumbs'] = (
            ('Home', 'home', {}, 1),
            ('All storages', 'storage_index', {}, 6))
        request.registry.settings['pyramid.default_locale_name'] = 'en'
        return Menu(request)

    # -------------------------------------------------------------------------
    def test_xhtml(self):
        """[u:lib.widget.Menu.xhtml]"""
        menu = self._make_one()
        xhtml = menu.xhtml()
        self.assertTrue(xhtml.startswith('<ul>'))
        self.assertTrue('<strong>Storages</strong>' in xhtml)
        self.assertTrue('href="/storage/index"' in xhtml)
        self.assertTrue(
            'href="/storage/browse/%s"' % self._storage_id in xhtml)
        self.assertTrue('<strong>Projects</strong>' in xhtml)
        self.assertTrue('href="/project/index"' in xhtml)
        self.assertTrue(
            'href="/project/dashboard/%s"' % self._project_id in xhtml)
        self.assertTrue('<strong>Administration</strong>' in xhtml)
        self.assertTrue('href="/user/admin"' in xhtml)
        self.assertTrue('href="/group/admin"' in xhtml)
        self.assertFalse('href="/storage/admin"' in xhtml)
        self.assertFalse('href="/project/admin"' in xhtml)
