# $Id: __init__.py 423387b2062e 2014/07/27 21:39:58 Patrick $
# pylint: disable = locally-disabled, R0904
"""Unit, integration, and functional testing."""

import unittest
import webtest
from os.path import join, dirname, normpath

from pyramid import testing


TEST_INI = normpath(join(dirname(__file__), '..', '..', 'development.ini'))


# =============================================================================
class PopulateOpts(object):
    """Dummy options for ``Populate`` constructor."""
    # pylint: disable = locally-disabled, R0903
    drop_tables = True
    no_pull = False
    reset_index = False
    no_index = False


# =============================================================================
class ModelTestCase(unittest.TestCase):
    """Base ``TestCase`` class with SqlAlchemy session."""
    # pylint: disable = locally-disabled, C0103

    # -------------------------------------------------------------------------
    def setUp(self):
        """Set SqlAlchemy session."""
        from logging import WARNING
        from ..models import DBSession
        from ..scripts.pfpopulate import Populate, LOG as pfpopulate_log
        from ..lib.vcs.hg import LOG as hg_log
        populate = Populate(PopulateOpts(), TEST_INI)
        pfpopulate_log.setLevel(WARNING)
        hg_log.setLevel(WARNING)
        populate.all()
        self.session = DBSession
        self.config = testing.setUp()

    # -------------------------------------------------------------------------
    def tearDown(self):
        """Undo the effects ``pyramid.testing.setUp()``."""
        self.session.remove()
        testing.tearDown()

    # -------------------------------------------------------------------------
    @classmethod
    def _make_request(cls):
        """Make a dummy request."""
        class DummyBreadcrumbs(object):
            """Dummy breadcrumb trail for :class:`DummyRequest`."""
            def add(self, title, length=0):
                """Add a crumb in breadcrumb trail."""
                pass

            @classmethod
            def current_path(cls):
                """Path of current page."""
                return '/'

        # pylint: disable = locally-disabled, W0212
        request = testing.DummyRequest()
        request.session['lang'] = 'en'
        request._LOCALE_ = request.session['lang']
        request.breadcrumbs = DummyBreadcrumbs()
        return request


# =============================================================================
class FunctionalTestCase(unittest.TestCase):
    """Base ``TestCase`` class with ``testapp`` attribute."""
    # pylint: disable = locally-disabled, C0103

    # -------------------------------------------------------------------------
    def setUp(self):
        """Set up test application."""
        self.testapp = TestApp('config:%s' % TEST_INI, relative_to='.')

    # -------------------------------------------------------------------------
    def tearDown(self):
        """Undo the effects ``pyramid.testing.setUp()``."""
        from ..models import DBSession
        del self.testapp
        DBSession.remove()


# =============================================================================
class TestApp(webtest.TestApp):
    """An extended ``TestApp`` class with login method."""

    # -------------------------------------------------------------------------
    def login(self, user_login):
        """Quick login.

        :param user_login: (string)
            User login.
        """
        csrf = self.get('/login').form.get('_csrf').value
        params = {'_csrf': csrf, 'login': user_login}
        self.post('/login_test', params, status=302)
