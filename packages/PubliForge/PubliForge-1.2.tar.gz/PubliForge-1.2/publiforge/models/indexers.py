# $Id: indexers.py e94a5cc5aef1 2014/08/19 07:57:32 Patrick $
"""SQLAlchemy-powered model definition for groups."""
# pylint: disable = locally-disabled, super-on-old-class

from lxml import etree
from cPickle import dumps, loads
from sqlalchemy import Column, ForeignKey, types
from sqlalchemy.orm import relationship

from ..lib.utils import _, normalize_spaces, make_id
from . import ID_LEN, LABEL_LEN, PATTERN_LEN, VALUE_LEN, Base, DBSession


INDEX_VALUE_TYPES = {
    'string': _('String'), 'integer': _('Integer'), 'date': _('Date'),
    'select': _('Closed list')}
EXTRACTOR_TYPES = {
    'regex': _('Regular expression'), 'xpath': 'XPath',
    'iim': _('Information Interchange Model')}
XML_NS = '{http://www.w3.org/XML/1998/namespace}'


# =============================================================================
class Indexer(Base):
    """SQLAlchemy-powered indexer model."""
    # pylint: disable = locally-disabled, star-args

    __tablename__ = 'indexers'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    indexer_id = Column(types.String(ID_LEN), primary_key=True)
    labels = Column(types.Text, nullable=False)
    value_type = Column(types.Enum(
        *INDEX_VALUE_TYPES.keys(), name='idx_value_type'))
    extractors = relationship('IndexerExtractor')
    values = relationship('IndexerValue')

    # -------------------------------------------------------------------------
    def __init__(self, indexer_id, labels, value_type):
        """Constructor method."""
        super(Indexer, self).__init__()
        self.indexer_id = make_id(indexer_id, 'token', ID_LEN)
        self.labels = dumps(labels)
        self.value_type = value_type

    # -------------------------------------------------------------------------
    def label(self, lang, default_lang='en'):
        """Return the label in language ``lang``.

        :param lang: (string)
            Asked language.
        :param default_lang: (string)
            Default language.
        :return: (string)
        """
        labels = loads(str(self.labels))
        labels = labels.get(lang) or labels.get(default_lang) or ''
        return labels.decode('utf8')

    # -------------------------------------------------------------------------
    @classmethod
    def load(cls, indexer_elt, error_if_exists=True):
        """Load a indexer from a XML file.

        :param indexer_elt: (:class:`lxml.etree.Element` instance)
            Indexer XML element.
        :param error_if_exists: (boolean, default=True)
            It returns an error if indexer already exists.
        :return: (:class:`pyramid.i18n.TranslationString` or ``None``)
            Error message or ``None``.
        """
        # Check if already exists
        indexer_id = make_id(indexer_elt.get('id'), 'token', ID_LEN)
        indexer = DBSession.query(cls).filter_by(indexer_id=indexer_id).first()
        if indexer is not None:
            if error_if_exists:
                return _('Indexer "${i}" already exists.', {'i': indexer_id})
            return

        # Create indexer
        labels = {}
        for item in indexer_elt.findall('label'):
            labels[item.get('%slang' % XML_NS)] = normalize_spaces(
                item.text).encode('utf8')
        indexer = cls(indexer_id, labels, indexer_elt.get('value'))

        # Add values
        if indexer.value_type == 'select':
            for item in indexer_elt.findall('option'):
                indexer.values.append(IndexerValue(
                    item.text, item.get('value')))

        # Add extractors
        for item in indexer_elt.findall('extractors/extractor'):
            indexer.extractors.append(IndexerExtractor(
                item.find('indexed').text, item.get('type'),
                item.find('parameter').text,
                item.find('parameter').get('limit')))

        DBSession.add(indexer)
        DBSession.commit()

    # -------------------------------------------------------------------------
    def xml(self):
        """Serialize a indexer to a XML representation.

        :return: (:class:`lxml.etree.Element`)
        """
        indexer_elt = etree.Element('indexer')
        indexer_elt.set('id', self.indexer_id)
        indexer_elt.set('value', self.value_type)
        labels = loads(str(self.labels))
        for lang in labels:
            elt = etree.SubElement(indexer_elt, 'label')
            elt.set('%slang' % XML_NS, lang)
            elt.text = labels[lang].decode('utf8')

        # Values
        if self.value_type == 'select':
            for value in self.values:
                elt = etree.SubElement(indexer_elt, 'option')
                elt.text = value.label
                if value.label != value.value:
                    elt.set('value', value.value)

        # Extractors
        elt = etree.SubElement(indexer_elt, 'extractors')
        for extractor in self.extractors:
            elt.append(extractor.xml())

        return indexer_elt


# =============================================================================
class IndexerExtractor(Base):
    """SQLAlchemy-powered indexer extractor class."""
    # pylint: disable = locally-disabled, R0903, W0142

    __tablename__ = 'indexers_extractors'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    indexer_id = Column(
        types.String(ID_LEN),
        ForeignKey('indexers.indexer_id', ondelete='CASCADE'),
        primary_key=True)
    extractor_id = Column(types.Integer, primary_key=True)
    indexed_files = Column(types.String(PATTERN_LEN))
    extractor_type = Column(
        types.Enum(*EXTRACTOR_TYPES.keys(), name='idx_extractor_type'))
    parameter = Column(types.String(VALUE_LEN))
    limit = Column(types.Integer)

    # -------------------------------------------------------------------------
    def __init__(self, indexed_files, extractor_type, parameter, limit=None):
        """Constructor method."""
        super(IndexerExtractor, self).__init__()
        self.indexed_files = indexed_files[0:64]
        self.extractor_type = extractor_type
        self.parameter = parameter or ''
        self.parameter = \
            extractor_type != 'iim' and self.parameter.strip()[0:96] \
            or normalize_spaces(self.parameter)[0:96]
        self.limit = limit or None

    # -------------------------------------------------------------------------
    def xml(self):
        """Serialize an extractor to a XML representation.

        :return: (:class:`lxml.etree.Element`)
        """
        extractor_elt = etree.Element('extractor', type=self.extractor_type)
        etree.SubElement(extractor_elt, 'indexed').text = self.indexed_files
        elt = etree.SubElement(extractor_elt, 'parameter')
        elt.text = self.parameter
        if self.limit:
            elt.set('limit', str(self.limit))

        return extractor_elt


# =============================================================================
class IndexerValue(Base):
    """SQLAlchemy-powered indexer value class."""
    # pylint: disable = locally-disabled, R0903, W0142

    __tablename__ = 'indexers_values'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    indexer_id = Column(
        types.String(ID_LEN),
        ForeignKey('indexers.indexer_id', ondelete='CASCADE'),
        primary_key=True)
    value_id = Column(types.Integer, primary_key=True)
    value = Column(types.String(VALUE_LEN), unique=True)
    label = Column(types.String(VALUE_LEN), unique=True)

    # -------------------------------------------------------------------------
    def __init__(self, label, value=None):
        """Constructor method."""
        super(IndexerValue, self).__init__()
        self.label = normalize_spaces(label, LABEL_LEN)
        self.value = value and normalize_spaces(value) or self.label
