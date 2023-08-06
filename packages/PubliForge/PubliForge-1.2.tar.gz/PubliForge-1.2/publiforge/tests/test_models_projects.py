# $Id: test_models_projects.py 423387b2062e 2014/07/27 21:39:58 Patrick $
# -*- coding: utf-8 -*-
# pylint: disable = locally-disabled, R0904
"""Tests of ``models.projects`` classes."""

from ..tests import ModelTestCase


# =============================================================================
class UnitTestModelsProjectsProject(ModelTestCase):
    """Unit test class for ``models.projects.Project``."""
    # pylint: disable = locally-disabled, C0103

    _project_id = 1000

    # -------------------------------------------------------------------------
    def tearDown(self):
        """Undo the effects ``pyramid.testing.setUp()``."""
        from ..models.projects import Project
        self.session.query(Project)\
            .filter_by(project_id=self._project_id).delete()
        ModelTestCase.tearDown(self)

    # -------------------------------------------------------------------------
    def _make_one(self):
        """Make an ``Project`` object."""
        from ..models.projects import Project
        project = Project(u'Les Misérables', u'Un roman de Virtor HUGO.')
        project.project_id = self._project_id
        return project

    # -------------------------------------------------------------------------
    def test_constructor(self):
        """[u:models.projects.Project.__init__]"""
        from ..models.projects import Project
        project1 = self._make_one()
        self.session.add(project1)
        self.session.commit()
        project2 = self.session.query(Project)\
            .filter_by(project_id=project1.project_id).first()
        self.assertNotEqual(project2, None)
        self.assertEqual(project2.project_id, project1.project_id)
        self.assertEqual(project2.label, project1.label)
        self.assertEqual(project2.status, project1.status)
        self.assertEqual(project2.deadline, project1.deadline)


# =============================================================================
class IntegrationTestModelsProjects(ModelTestCase):
    """Integration test class for ``models.projects``."""
    # pylint: disable = locally-disabled, C0103

    _project_id = 1000
    _user_id = 1000

    # -------------------------------------------------------------------------
    def tearDown(self):
        """Undo the effects ``pyramid.testing.setUp()``."""
        from ..models.users import User
        from ..models.projects import Project
        self.session.query(User).filter_by(user_id=self._user_id).delete()
        self.session.query(Project)\
            .filter_by(project_id=self._project_id).delete()
        self.session.commit()
        ModelTestCase.tearDown(self)

    # -------------------------------------------------------------------------
    def _make_project(self):
        """Make a ``Project`` object."""
        # pylint: disable = locally-disabled, E1101
        from ..models.projects import Project
        project = Project(u'Les Misérables', u'Un roman de Victor HUGO.')
        project.project_id = self._project_id
        return project

    # -------------------------------------------------------------------------
    def _make_user(self):
        """Make an ``User`` object."""
        from ..models.users import User
        user = User({'encryption': 'seekrit'}, '_test_user', status='active',
                    password='mypassword', name=u'Marc HINDÉLAIBILE',
                    email='test@prismallia.fr', lang='en')
        user.user_id = self._user_id
        return user

    # -------------------------------------------------------------------------
    def test_remove_user(self):
        """[i:models.projects] remove user"""
        from ..models.users import User
        from ..models.projects import ProjectUser
        project = self._make_project()
        user = self._make_user()
        self.session.add(user)
        project.users.append(ProjectUser(project.project_id, self._user_id))
        self.session.add(project)
        self.session.commit()
        self.assertEqual(len(project.users), 1)
        project_user = self.session.query(ProjectUser).filter_by(
            project_id=project.project_id, user_id=self._user_id).first()
        self.assertFalse(project_user.in_menu)
        self.session.query(User).filter_by(user_id=self._user_id).delete()
        self.session.commit()
        self.assertEqual(len(project.users), 0)
