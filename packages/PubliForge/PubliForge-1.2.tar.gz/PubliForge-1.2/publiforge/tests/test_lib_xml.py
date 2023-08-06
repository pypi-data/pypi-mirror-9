# $Id: test_lib_xml.py 16b427c9198b 2015/02/21 08:29:03 Patrick $
# -*- coding: utf-8 -*-
# pylint: disable = locally-disabled, R0904
"""Tests of ``lib.xml`` classes and functions."""

import unittest
import os
from os.path import join, dirname

XML_FILE = join(
    dirname(__file__), '..', 'Processors', 'PublidocValid', 'processor.xml')
INI_FILE = join(
    dirname(__file__), '..', 'Processors', 'Publidoc2XHtml', 'leprisme.ini')


# =============================================================================
class UnitTestLibUtilsLoad(unittest.TestCase):
    """Unit test class for ``lib.xml.load``."""

    # -------------------------------------------------------------------------
    @classmethod
    def _call_fut(cls, filename, relaxngs=None, data=None):
        """Call function under test."""
        from ..lib.xml import load
        if relaxngs is None:
            relaxngs = {
                'publiforge':
                join(dirname(__file__), '..', 'RelaxNG', 'publiforge.rng')}
        return load(filename, relaxngs, data)

    # -------------------------------------------------------------------------
    def test_not_well_formed(self):
        """[u:lib.xml.load] not well-formed XML"""
        tree = self._call_fut(INI_FILE)
        self.assertTrue(isinstance(tree, basestring))
        self.assertTrue('is not well-formed' in tree)

    # -------------------------------------------------------------------------
    def test_invalid(self):
        """[u:lib.xml.load] invalid XML"""
        with open(XML_FILE, 'r') as hdl:
            data = hdl.read().replace('processor', 'motor')
        tree = self._call_fut(XML_FILE, data=data)
        self.assertTrue(isinstance(tree, basestring))
        self.assertTrue('Line' in tree)

    # -------------------------------------------------------------------------
    def test_valid_xml(self):
        """[u:lib.xml.load] valid XML"""
        tree = self._call_fut(XML_FILE)
        self.assertFalse(isinstance(tree, basestring))


# =============================================================================
class UnitTestLibXmlXpathCamelCase(unittest.TestCase):
    """Unit test class for ``lib.xml.xpath_camel_case``."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.xml.xpath_camel_case]"""
        from ..lib.xml import xpath_camel_case
        self.assertEqual(
            xpath_camel_case(1, 'test'), 'Test')
        self.assertEqual(
            xpath_camel_case(0, 'pdoc2html'), 'Pdoc2Html')
        self.assertEqual(
            xpath_camel_case(0, 'my_way test-all'), 'MyWayTest-All')
        self.assertEqual(
            xpath_camel_case(0, '../ tests/lib/utils'), '../Tests/lib/utils')


# =============================================================================
class UnitTestLibXmlXpathMakeId(unittest.TestCase):
    """Unit test class for ``lib.xml.xpath_make_id``."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.xml.xpath_make_id]"""
        from ..lib.xml import xpath_make_id
        self.assertEqual(
            xpath_make_id(0, 'Test___Tes*t;!?.', 'token'), 'test_tes_t_')
        self.assertEqual(
            xpath_make_id(0, '../tests/lib/utils', 'standard'),
            '_tests_lib_utils')


# =============================================================================
class UnitTestLibXmlXpathRelpath(unittest.TestCase):
    """Unit test class for ``lib.xml.xpath_relpath``."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.xml.xpath_relpath]"""
        from ..lib.xml import xpath_relpath
        self.assertEqual(
            xpath_relpath(0, 'tests/lib/utils', os.curdir),
            'tests/lib/utils')
        self.assertEqual(
            xpath_relpath(0, '/tests/lib/utils', os.curdir),
            '../../../../tests/lib/utils')
        self.assertEqual(
            xpath_relpath(0, '/tests/lib/utils', '~/Devel'),
            '../../../../../../tests/lib/utils')
        self.assertEqual(
            xpath_relpath(0, 'tests/lib/utils', 'Devel/PubliForge'),
            '../../tests/lib/utils')
