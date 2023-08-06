# $Id: test_lib_utils.py 2ae0cc6eeb9b 2014/08/08 07:12:01 Patrick $
# -*- coding: utf-8 -*-
# pylint: disable = locally-disabled, R0904
"""Tests of ``lib.utils`` classes and functions."""

import unittest
from os.path import join, dirname

INI_FILE = join(
    dirname(__file__), '..', 'Processors', 'Publidoc2XHtml', 'leprisme.ini')
CONTENT_DIR = join(dirname(__file__), '..', 'Processors', 'PublidocValid')
CONTENT_EXCLUDE = ('.hg', 'publiset.rng')


# =============================================================================
class UnitTestLibUtilsConfigGet(unittest.TestCase):
    """Unit test class for ``lib.utils.config_get``."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.utils.config_get]"""
        from ConfigParser import ConfigParser
        from ..lib.utils import config_get
        config = ConfigParser({'here': dirname(INI_FILE)})
        config.read(INI_FILE)
        self.assertEqual(config_get(config, 'Input', 'file_regex'), r'\.xml$')
        self.assertEqual(config_get(config, 'Input', 'foo', 'bar'), 'bar')


# =============================================================================
class UnitTestLibUtilsCopyContent(unittest.TestCase):
    """Unit test class for ``lib.utils.copy_content``."""
    # pylint: disable = locally-disabled, C0103

    # -------------------------------------------------------------------------
    def __init__(self, method_name='runTest'):
        """Constructor method."""
        super(UnitTestLibUtilsCopyContent, self).__init__(method_name)
        self._tmp_dir = None

    # -------------------------------------------------------------------------
    def setUp(self):
        """Create a temporary directory."""
        from tempfile import mkdtemp
        self.tearDown()
        self._tmp_dir = mkdtemp()

    # -------------------------------------------------------------------------
    def tearDown(self):
        """Undo the effects ``pyramid.testing.setUp()``."""
        from os.path import exists
        from shutil import rmtree
        if self._tmp_dir is not None and exists(self._tmp_dir):
            rmtree(self._tmp_dir)
        self._tmp_dir = None

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.utils.copy_content]"""
        from os import walk
        from os.path import exists, relpath
        from ..lib.utils import copy_content
        copy_content(CONTENT_DIR, self._tmp_dir, CONTENT_EXCLUDE)
        for path, dirs, files in walk(CONTENT_DIR):
            for name in dirs + files:
                copy = join(self._tmp_dir, relpath(path, CONTENT_DIR), name)
                if name in CONTENT_EXCLUDE:
                    self.assertFalse(exists(copy))
                else:
                    self.assertTrue(exists(copy))


# =============================================================================
class UnitTestLibUtilsCamelCase(unittest.TestCase):
    """Unit test class for ``lib.utils.camel_case``."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.utils.camel_case]"""
        from ..lib.utils import camel_case
        self.assertEqual(camel_case('pdoc2html'), 'Pdoc2Html')
        self.assertEqual(camel_case('LaTeX'), 'LaTeX')
        self.assertEqual(camel_case('laTeX'), 'LaTeX')
        self.assertEqual(camel_case('my_way'), 'MyWay')
        self.assertEqual(camel_case('my way'), 'MyWay')
        self.assertEqual(camel_case('my-way'), 'My-Way')


# =============================================================================
class UnitTestLibUtilsHashSha(unittest.TestCase):
    """Unit test class for ``lib.utils.hash_sha``."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.utils.hash_sha]"""
        from ..lib.utils import hash_sha
        self.assertEqual(hash_sha('protectme', None),
                         '360a06e80743072020f69f2129c4933ea29f879f')
        self.assertEqual(hash_sha('protectme', 'seekrit'),
                         'e50267004c95597d525f9a16e68d046c80eb0ded')
        self.assertEqual(hash_sha(u'protègemoi', None),
                         'c4eb986ca838b6e2dc6c4b1bdfa31142ea565a84')


# =============================================================================
class UnitTestLibUtilsEncrypt(unittest.TestCase):
    """Unit test class for ``lib.utils.encrypt``."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.utils.encrypt]"""
        from ..lib.utils import encrypt
        self.assertEqual(
            encrypt('protectme', None), 'XzgU2PN974c3yYOp4FsJzw==')
        self.assertEqual(
            encrypt('protectme', 'seekrit'), 'B/48LdYirNqHOFq3dMIWQA==')
        self.assertEqual(
            encrypt(u'protègemoi', 'seekrit'), 'GoJ3XiMjxaXqm6eDr9anfg==')


# =============================================================================
class UnitTestLibUtilsDecrypt(unittest.TestCase):
    """Unit test class for ``lib.utils.decrypt``."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.utils.decrypt]"""
        from ..lib.utils import decrypt
        self.assertEqual(
            decrypt('XzgU2PN974c3yYOp4FsJzw==', None), 'protectme')
        self.assertEqual(
            decrypt('B/48LdYirNqHOFq3dMIWQA==', 'seekrit'), 'protectme')
        self.assertEqual(
            decrypt('GoJ3XiMjxaXqm6eDr9anfg==', 'seekrit').decode('utf8'),
            u'protègemoi')


# =============================================================================
class UnitTestLibUtilsSettingsGetList(unittest.TestCase):
    """Unit test class for ``lib.utils.settings_get_list``."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.utils.settings_get_list]"""
        from ..lib.utils import settings_get_list
        self.assertEqual(
            settings_get_list({}, ''), [])
        self.assertEqual(
            settings_get_list({}, 'option', ['vide']), ['vide'])
        self.assertEqual(
            settings_get_list({'option1': '*', 'option2': 'tu'}, 'option'), [])
        self.assertEqual(
            settings_get_list({'option1': '*', 'option2': 'test'}, 'option2'),
            ['test'])
        self.assertEqual(
            settings_get_list({'option1': '*', 'option2': 'test, test2'},
                              'option2'), ['test', 'test2'])


# =============================================================================
class UnitTestLibUtilsConfigGetList(unittest.TestCase):
    """Unit test class for ``lib.utils.config_get_list``."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.utils.config_get_list]"""
        from ConfigParser import ConfigParser
        from ..lib.utils import config_get_list
        config = ConfigParser({'here': dirname(INI_FILE)})
        config.read(INI_FILE)
        self.assertEqual(
            config_get_list(config, 'Input', 'file_regex'), [r'\.xml$'])
        self.assertEqual(
            config_get_list(config, 'Input', 'none', 'false'), 'false')
        self.assertEqual(
            config_get_list(config, 'Input', 'none'), [])
        self.assertEqual(
            config_get_list(config, 'Input', 'image.ext'),
            [u'svg', u'png', u'tif', u'tiff', u'jpg', u'jpeg',
             u'pdf', u'eps', u'gif'])


# =============================================================================
class UnitTestLibUtilsNormalizeName(unittest.TestCase):
    """Unit test class for ``lib.utils.normalize_name``."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.utils.normalize_name]"""
        from ..lib.utils import normalize_name
        self.assertEqual(
            normalize_name('__test_____'), '_test_')
        self.assertEqual(
            normalize_name('__?t es t!;*_,'), '_t_es_t_')
        self.assertEqual(
            normalize_name('__?test! ; *_,'), '_test_')
        self.assertEqual(
            normalize_name(' , '), '_')
        self.assertEqual(
            normalize_name('     '), '_')


# =============================================================================
class UnitTestLibUtilsSizeLabel(unittest.TestCase):
    """Unit test class for ``lib.utils.size_label``."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.utils.size_label]"""
        from ..lib.utils import size_label
        self.assertEqual(
            size_label(133497, True), u'${n} items')
        self.assertEqual(
            size_label(0, False), '0 o')
        self.assertEqual(
            size_label(1024, False), '1.0 Kio')
        self.assertEqual(
            size_label(1048576, False), '1.0 Mio')
        self.assertEqual(
            size_label(1073741824, False), '1.0 Gio')


# =============================================================================
class UnitTestLibUtilsRst2xhtml(unittest.TestCase):
    """Unit test class for ``lib.utils.rst2xhtml``."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.utils.rst2xhtml]"""
        from ..lib.utils import rst2xhtml
        self.assertEqual(
            rst2xhtml(''), None)
        self.assertEqual(
            rst2xhtml('test'), '<p>test</p>\n')
        self.assertEqual(
            rst2xhtml('*emphasis*'), u'<p><em>emphasis</em></p>\n')
        self.assertEqual(
            rst2xhtml('``inline literal``'),
            u'<p><tt class="docutils literal">inline literal</tt></p>\n')


# =============================================================================
class UnitTestLibUtilsExecute(unittest.TestCase):
    """Unit test class for ``lib.utils.execute``."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.utils.execute]"""
        from ..lib.utils import execute
        self.assertEqual(
            execute(['echo', 'test'], None, False), (u'test', ''))
        self.assertEqual(
            execute(['echo', 'test'], 'cwd', True),
            ('', u'"${c}" failed: ${e}'))
        self.assertEqual(
            execute(['echo', 'test'], None, True), (u'test', u'"${c}" failed'))
        self.assertEqual(
            execute(['echo', 'test1', 'test2'], None, False),
            (u'test1 test2', ''))


# =============================================================================
class UnitTestLibUtilsWrap(unittest.TestCase):
    """Unit test class for ``lib.utils.wrap``."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.utils.wrap]"""
        from ..lib.utils import wrap
        self.assertEqual(
            wrap('test test2', 1, 0), u't\ne\ns\nt\nt\ne\ns\nt\n2')
        self.assertEqual(
            wrap('test         test2', 1, 0), u't\ne\ns\nt\nt\ne\ns\nt\n2')
        self.assertEqual(
            wrap('test         test2', 2, 0), u'te\nst\nte\nst\n2')
        self.assertEqual(
            wrap('test         test2', indent=10),
            u'\n          test         test2\n        ')


# =============================================================================
class UnitTestLibUtilsNormalizeSpaces(unittest.TestCase):
    """Unit test class for ``lib.utils.normalize_spaces``."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.utils.normalize_spaces]"""
        from ..lib.utils import normalize_spaces
        self.assertEqual(
            normalize_spaces(None, None), None)
        self.assertEqual(
            normalize_spaces(None, 2), None)
        self.assertEqual(
            normalize_spaces('test test1       test2  _    ', None),
            'test test1 test2 _')
        self.assertEqual(
            normalize_spaces('test test1       test2  _    ', 9),
            'test test')


# =============================================================================
class UnitTestLibUtilsMakeId(unittest.TestCase):
    """Unit test class for ``lib.utils.make_id``."""

    # -------------------------------------------------------------------------
    def test_it(self):
        """[u:lib.utils.make_id]"""
        from ..lib.utils import make_id
        self.assertEqual(
            make_id(''), '')
        self.assertEqual(
            make_id('Test___Tes*t;!?'), 'test___tes*t;!?')
        self.assertEqual(
            make_id('Test___Tes*t;!?', 'standard'), 'test_tes_t_')
        self.assertEqual(
            make_id('Test___Tes*t;!?', 'token'), 'test_tes_t_')
        self.assertEqual(
            make_id('Test___Tes*t;!?', 'class'), 'Test_Tes_t_')
        self.assertEqual(
            make_id('Test___Tes*t;!?', 'class', 6), 'Test_T')
