# $Id$
"""Publiset management."""

from os.path import join, basename, splitext, normpath, relpath
from lxml import etree
from copy import deepcopy

from ...utils import _
from ...xml import XML_NS, load

PUBLIDOC_VERSION = '1.0'
PUBLISET_VERSION = '1.0'


# =============================================================================
class Publiset(object):
    """Class for Publiset management."""

    # -------------------------------------------------------------------------
    def __init__(self, processor, base_path):
        """Constructor method.

        :param processor: (:class:`~.lib.processor.leprisme.Processor` object)
            Processor object on which it depends.
        :param base_path: (string)
            Base path for files in publiset.
        """
        self._processor = processor
        self._base_path = base_path
        self._pi_source = False

    # -------------------------------------------------------------------------
    def fullname(self, file_elt):
        """Find the full path of a file from a file tag.

        :param file_elt: (etree.Element object)
             File element.
        :return: (string)
             Full path name.
        """
        elt = file_elt
        while elt is not None and elt.get('path') is None:
            elt = elt.getparent()

        if elt is None or elt.get('path') is None:
            return join(self._base_path, file_elt.text)
        return normpath(join(
            self._base_path, elt.get('path'), file_elt.text))

    # -------------------------------------------------------------------------
    def compose(self, filename, set_root):
        """Compose an XML document from a publiset XML composition.

        :param filename: (string)
            Name of the composition file.
        :param set_root: (:class:`lxml.etree.Element` instance)
            ``composition`` element.
        :return: (etree.ElementTree object)
            Document tree or ``None``.
        """
        # Document root element
        doc_root = self._doc_element(
            set_root, 'publidoc', {'version': PUBLIDOC_VERSION})
        self._pi_source = set_root.get('pi-source')

        # Browse structure
        for elt in set_root.xpath('*|processing-instruction()'):
            if not self._append(elt, doc_root):
                return
        doc_root = etree.ElementTree(doc_root)

        # Validate
        if self._processor.config('Input', 'validate') == 'true':
            doc_root = load(
                filename, self._processor.relaxngs, etree.tostring(doc_root))
            if isinstance(doc_root, basestring):
                self._processor.build.stopped(doc_root, 'a_error')
                return

        return doc_root

    # -------------------------------------------------------------------------
    @classmethod
    def create(cls, element):
        """Create an empty ``publiset`` document and fill it with ``element``.

        :param element: (:class:`lxml.etree.Element` instance)
            Main element.
        :return: (etree.ElementTree)
        """
        root = etree.Element('publiset', version=PUBLISET_VERSION)
        root.append(element)
        return etree.ElementTree(root)

    # -------------------------------------------------------------------------
    def _append(self, set_current, doc_current):
        """Append ``set_current`` to ``doc_current`` element, converting tag
        and attribute names.

        :param set_current: (:class:`lxml.etree.Element` instance)
            Publiset element.
        :param doc_current: (:class:`lxml.etree.Element` instance)
            Target document element.
        :return: (boolean)
        """
        # pylint: disable = locally-disabled, R0911
        # Processing instruction
        if not isinstance(set_current.tag, basestring):
            doc_current.append(set_current)
            return True

        # File
        if set_current.tag == 'file':
            return self._append_file(set_current, doc_current)

        # Browse
        doc_elt = self._doc_element(set_current)
        for set_elt in set_current.xpath('*|processing-instruction()'):
            if not self._append(set_elt, doc_elt):
                return False
        if set_current.get('transform') is None:
            doc_current.append(doc_elt)
            return True

        # Transform
        xslfile = join(self._processor.build.path, 'Processor', 'Xsl',
                       set_current.get('transform'))
        try:
            transform = etree.XSLT(etree.parse(xslfile))
        except (IOError, etree.XSLTParseError, etree.XMLSyntaxError) as err:
            self._processor.build.stopped(
                str(err).replace(self._processor.build.path, '..'))
            return False
        try:
            for doc_elt in transform(doc_elt)\
                    .xpath('/*|/processing-instruction()'):
                doc_current.append(doc_elt)
        except (etree.XSLTApplyError, AssertionError) as err:
            self._processor.build.stopped(err, 'a_error')
            return False
        return True

    # -------------------------------------------------------------------------
    def _append_file(self, file_elt, doc_current):
        """Append file content as child of ``doc_current``.

        :param file_elt: (:class:`lxml.etree.Element` instance)
             File element.
        :param doc_current: (:class:`lxml.etree.Element` instance)
            Target document element.
        :return: (boolean)
        """
        # Load file
        # pylint: disable = locally-disabled, E1103, R0911
        if file_elt.text is None:
            self._processor.build.stopped(_('Empty <file/> tag.'), 'a_warn')
            return True
        relaxngs = self._processor.relaxngs \
            if self._processor.config('Input', 'validate') == 'true' else None
        filename = self.fullname(file_elt)
        if not filename.startswith(self._processor.build.data_path):
            self._processor.build.stopped(_(
                '${f}: file outside storage area', {'f': basename(filename)}))
            return False
        tree = load(filename, relaxngs)
        if isinstance(tree, basestring):
            self._processor.build.stopped(tree, 'a_error')
            return False

        # PI source
        if self._pi_source:
            doc_current.append(
                etree.ProcessingInstruction(
                    'source',
                    relpath(filename, self._processor.build.data_path)))

        # How to compose?...
        set_elt = file_elt
        while set_elt is not None and set_elt.get('xslt') is None \
                and set_elt.get('xpath') is None:
            set_elt = set_elt.getparent()

        # ...copy
        if set_elt is None:
            self._append_file_element(
                doc_current, deepcopy(tree.getroot()),
                file_elt.get('argument'))
        # ...XSL transformation
        elif set_elt.get('xslt'):
            return self._append_file_xslt(
                filename, tree, set_elt.get('xslt'), doc_current,
                file_elt.get('argument'))
        # ...XPath
        else:
            try:
                for child in tree.xpath(set_elt.get('xpath')):
                    self._append_file_element(
                        doc_current, child, file_elt.get('argument'))
            except etree.XPathEvalError as err:
                self._processor.build.stopped('XPath: %s' % err, 'a_error')
                return False

        return True

    # -------------------------------------------------------------------------
    @classmethod
    def _append_file_element(cls, doc_current, child, argument=None):
        """Append a file element as child of ``doc_current`` with, eventually,
        a <?argument ?> processing instruction with the content of
        ``argument``.

        :param doc_current: (:class:`lxml.etree.Element` instance)
            Target document element.
        :param child: (:class:`lxml.etree.Element` instance)
            Element to append.
        :param argument: (string, optional)
            Argument for a processing instruction.
        """
        if argument is not None:
            child.insert(
                0, etree.ProcessingInstruction('argument', argument.strip()))
        doc_current.append(child)

    # -------------------------------------------------------------------------
    def _append_file_xslt(
            self, filename, tree, xsl_file, doc_current, argument=None):
        """Append a XSL transformation file element as child of ``doc_current``
        with, eventually, a <?argument ?> processing instruction.

        :param filename: (string)
            Full path to the current file.
        :param tree: (:class:`lxml.etree.ElementTree` instance)
            DOM of the file to process.
        :param xsl_file: (string)
            Name of the XSL file.
        :param argument: (string, optional)
            Argument for a processing instruction.
        :return: (boolean)
        """
        xsl_file = join(
            self._processor.build.path, 'Processor', 'Xsl', xsl_file)
        try:
            xslt = etree.XSLT(etree.parse(xsl_file))
        except (IOError, etree.XSLTParseError, etree.XMLSyntaxError) as error:
            self._processor.build.stopped(
                str(error).replace(self._processor.build.path, '..'))
            return False

        fid = '"%s"' % splitext(basename(filename))[0]
        try:
            for child in xslt(tree, fid=fid)\
                    .xpath('/*|/comment()|/processing-instruction()'):
                self._append_file_element(doc_current, child, argument)
        except (etree.XSLTApplyError, AssertionError) as error:
            self._processor.build.stopped(error, 'a_error')
            return False
        return True

    # -------------------------------------------------------------------------
    @classmethod
    def _doc_element(cls, set_elt, default_tag=None, default_atts=None):
        """Create a document element from a set element according to its ``as``
        and ``attributes`` attributes.

        :param set_elt: (:class:`lxml.etree.Element` instance)
            Source element
        :param default_tag: (string)
            If ``default_tag`` is None and ``as`` attribute doesn't exist, the
            ``set_elt`` name is used as tag name.
        :param default_atts: (dictionary)
            If ``default_atts`` is None and ``attributes`` attribute doesn't
            exist, ``set_elt`` attributes are copied.
        :return: (:class:`lxml.etree.ElementTree`)
        """
        # Tag
        if default_tag is None:
            default_tag = set_elt.tag
        doc_elt = etree.Element(set_elt.get('as', default_tag))

        # Attributes
        atts = set_elt.get('attributes', '').split()
        if atts:
            atts = dict([(i.split('=')[0], i.split('=')[1]) for i in atts])
        else:
            atts = default_atts or set_elt.attrib
        for att, value in atts.items():
            if att not in \
                    ('as', 'attributes', 'transform', 'path', 'xslt', 'xpath'):
                doc_elt.set(att.replace('xml:', XML_NS), value)

        # Text
        doc_elt.text = set_elt.text
        doc_elt.tail = set_elt.tail

        return doc_elt
