# $Id: indexer.py 423387b2062e 2014/07/27 21:39:58 Patrick $
# pylint: disable = locally-disabled, C0322
"""Indexer view callables."""

from cPickle import loads, dumps
from colander import Mapping, SchemaNode, String, Integer
from colander import All, Length, Regex, OneOf
from sqlalchemy import desc

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPForbidden

from ..lib.utils import _, has_permission, make_id, normalize_spaces
from ..lib.utils import settings_get_list
from ..lib.xml import upload_configuration, export_configuration
from ..lib.viewutils import get_action
from ..lib.form import Form
from ..lib.widget import Paging, TabSet
from ..models import ID_LEN, VALUE_LEN, PATTERN_LEN, DBSession, close_dbsession
from ..models.indexers import INDEX_VALUE_TYPES, EXTRACTOR_TYPES
from ..models.indexers import Indexer, IndexerExtractor, IndexerValue


INDEXER_SETTINGS_TABS = (
    _('Description'), _('Extractors'), _('Closed list of values'))


# =============================================================================
class IndexerView(object):
    """Class to manage indexers."""

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        request.add_finished_callback(close_dbsession)
        self._request = request

    # -------------------------------------------------------------------------
    @view_config(
        route_name='indexer_admin', renderer='../Templates/idx_admin.pt',
        permission='idx.update')
    def admin(self):
        """List indexers for administration purpose."""
        action, items = get_action(self._request)
        if action == 'imp!':
            upload_configuration(self._request, 'idx_manager', 'indexer')
            if 'search' in self._request.session:
                del self._request.session['search']
            self._request.registry['handler'].delete_index()
            action = ''
        elif action[0:4] == 'del!':
            if not has_permission(self._request, 'idx_manager'):
                raise HTTPForbidden()
            DBSession.query(Indexer).filter(
                Indexer.indexer_id.in_(items)).delete('fetch')
            DBSession.commit()
            if 'search' in self._request.session:
                del self._request.session['search']
            action = ''
            if 'search' in self._request.session:
                del self._request.session['search']
            self._request.registry['handler'].delete_index()
        elif action[0:4] == 'exp!':
            return self._export_indexers(items)

        paging, defaults = self._paging_indexers()
        lang = self._request.session['lang']
        default_lang = self._request.registry.settings[
            'pyramid.default_locale_name']
        labels = dict([
            (k.indexer_id, k.label(lang, default_lang)) for k in paging])
        form = Form(self._request, defaults=defaults)

        depth = (self._request.breadcrumbs.current_path() ==
                 self._request.route_path('site_admin') and 3) or 2
        self._request.breadcrumbs.add(_('Indexing administration'), depth)
        return {
            'form': form, 'paging': paging, 'action': action, 'labels': labels,
            'i_editor': has_permission(self._request, 'idx_editor'),
            'i_manager': has_permission(self._request, 'idx_manager'),
            'INDEX_VALUE_TYPES': INDEX_VALUE_TYPES}

    # -------------------------------------------------------------------------
    @view_config(
        route_name='indexer_view', renderer='../Templates/idx_view.pt',
        permission='idx.read')
    def view(self):
        """Show indexer settings."""
        indexer_id = self._request.matchdict.get('indexer_id')
        action = get_action(self._request)[0]
        if action == 'exp!':
            return self._export_indexers((indexer_id,))

        indexer = DBSession.query(Indexer).filter_by(
            indexer_id=indexer_id).first()
        if indexer is None:
            raise HTTPNotFound()
        labels = loads(str(indexer.labels))
        label = indexer.label(
            self._request.session['lang'],
            self._request.registry.settings['pyramid.default_locale_name'])
        tab_set = TabSet(self._request, INDEXER_SETTINGS_TABS)

        self._request.breadcrumbs.add(
            _('Indexer settings'), replace=self._request.route_path(
                'indexer_edit', indexer_id=indexer.indexer_id))
        return {
            'form': Form(self._request), 'tab_set': tab_set,
            'indexer': indexer, 'labels': labels, 'label': label,
            'INDEX_VALUE_TYPES': INDEX_VALUE_TYPES,
            'EXTRACTOR_TYPES': EXTRACTOR_TYPES,
            'i_editor': has_permission(self._request, 'idx_editor')}

    # -------------------------------------------------------------------------
    @view_config(
        route_name='indexer_create', renderer='../Templates/idx_edit.pt',
        permission='idx.create')
    def create(self):
        """Create an indexer."""
        default_lang = self._request.registry.settings[
            'pyramid.default_locale_name']
        labels = {default_lang: None}
        if self._request.session['lang'] != default_lang:
            labels[self._request.session['lang']] = None
        form, tab_set = self._settings_form(default_lang, labels)

        if form.validate():
            indexer = self._create(labels, form.values)
            if indexer is not None:
                if 'search' in self._request.session:
                    del self._request.session['search']
                self._request.registry['handler'].delete_index()
                self._request.breadcrumbs.pop()
                return HTTPFound(self._request.route_path(
                    'indexer_edit', indexer_id=indexer.indexer_id))
        if form.has_error():
            self._request.session.flash(_('Correct errors.'), 'alert')

        self._request.breadcrumbs.add(_('Indexer creation'))
        return {
            'form': form, 'tab_set': tab_set, 'indexer': None,
            'labels': labels, 'default_lang': default_lang,
            'INDEX_VALUE_TYPES': INDEX_VALUE_TYPES}

    # -------------------------------------------------------------------------
    @view_config(
        route_name='indexer_edit', renderer='../Templates/idx_edit.pt',
        permission='idx.update')
    def edit(self):
        """Edit indexer settings."""
        # Action
        indexer_id = self._request.matchdict.get('indexer_id')
        action = get_action(self._request)[0]
        if action[0:4] == 'del!':
            DBSession.query(IndexerExtractor).filter_by(
                indexer_id=indexer_id, extractor_id=int(action[4:]))\
                .delete()
            DBSession.commit()
            if 'search' in self._request.session:
                del self._request.session['search']
            self._request.registry['handler'].delete_index()
        elif action[0:4] == 'dvl!':
            DBSession.query(IndexerValue).filter_by(
                indexer_id=indexer_id, value_id=int(action[4:])).delete()
            DBSession.commit()
            if 'search' in self._request.session:
                del self._request.session['search']
            self._request.registry['handler'].delete_index()

        # Environment
        indexer = DBSession.query(Indexer).filter_by(
            indexer_id=indexer_id).first()
        if indexer is None:
            raise HTTPNotFound()
        default_lang = self._request.registry.settings[
            'pyramid.default_locale_name']
        labels = loads(str(indexer.labels))
        for lang in settings_get_list(
                self._request.registry.settings, 'languages'):
            if lang not in labels:
                labels[lang] = None
        label = indexer.label(self._request.session['lang'], default_lang)
        form, tab_set = self._settings_form(default_lang, labels, indexer)

        # Save
        view_path = self._request.route_path(
            'indexer_view', indexer_id=indexer.indexer_id)
        if action == 'sav!' and form.validate(indexer) \
                and self._save(labels, indexer, form.values):
            if 'search' in self._request.session:
                del self._request.session['search']
            self._request.registry['handler'].delete_index()
            return HTTPFound(view_path)
        if form.has_error():
            self._request.session.flash(_('Correct errors.'), 'alert')

        # Breadcrumbs
        self._request.breadcrumbs.add(_('Indexer settings'), replace=view_path)

        return {
            'form': form, 'action': action, 'tab_set': tab_set,
            'indexer': indexer, 'labels': labels, 'label': label,
            'default_lang': default_lang,
            'INDEX_VALUE_TYPES': INDEX_VALUE_TYPES,
            'EXTRACTOR_TYPES': EXTRACTOR_TYPES}

    # -------------------------------------------------------------------------
    def _paging_indexers(self):
        """Return a :class:`~.widget.Paging` object filled with indexers.

        :return: (tuple)
            A tuple such as ``(paging, filters)`` where ``paging`` is a
            :class:`~.widget.Paging` object and ``filters`` a dictionary of
            filters.
        """
        # Parameters
        params = Paging.params(self._request, 'indexers', '+indexer_id')

        # Query
        query = DBSession.query(Indexer)
        if 'f_id' in params:
            query = query.filter(
                Indexer.indexer_id.like('%%%s%%' % params['f_id'].lower()))

        # Order by
        oby = 'indexers.%s' % params['sort'][1:]
        query = query.order_by(desc(oby) if params['sort'][0] == '-' else oby)

        return Paging(self._request, 'indexers', query), params

    # -------------------------------------------------------------------------
    def _export_indexers(self, indexer_ids):
        """Export indexers.

        :param user_ids: (list)
            List of user IDs to export.
        :return: (:class:`pyramid.response.Response` instance or ``''``)
        """
        elements = []
        for indexer in DBSession.query(Indexer)\
                .filter(Indexer.indexer_id.in_(indexer_ids))\
                .order_by('indexer_id'):
            elements.append(indexer.xml())

        name = '%s_indexers.pfidx' % self._request.registry.settings.get(
            'skin.label', 'publiforge')
        return export_configuration(elements, name)

    # -------------------------------------------------------------------------
    def _settings_form(self, default_lang, labels, indexer=None):
        """Return a indexer settings form.

        :param default_lang: (string)
            Default language.
        :param labels: (dictionary)
            Label in several languages.
        :param indexer: (:class:`~..models.indexers.Indexer` instance,
            optional) Current indexer object.
        :return: (tuple)
            A tuple such as ``(form, tab_set)``.
        """
        # Schema
        defaults = {}
        schema = SchemaNode(Mapping())
        if indexer is None:
            schema.add(SchemaNode(
                String(), name='indexer_id', validator=All(
                    Regex(r'^[a-z_][a-z0-9-_]+$'), Length(max=ID_LEN))))
        for lang in labels:
            if lang == default_lang:
                schema.add(SchemaNode(String(), name='label_%s' % lang))
            else:
                schema.add(SchemaNode(
                    String(), name='label_%s' % lang, missing=None))
            if labels[lang]:
                defaults['label_%s' % lang] = labels[lang].decode('utf8')
        schema.add(SchemaNode(
            String(), name='value_type',
            validator=OneOf(INDEX_VALUE_TYPES.keys())))

        # Extractors
        if indexer is not None:
            for extractor in indexer.extractors:
                schema.add(SchemaNode(
                    String(), name='ex_%d_files' % extractor.extractor_id,
                    validator=Length(max=PATTERN_LEN)))
                schema.add(SchemaNode(
                    String(), name='ex_%d_type' % extractor.extractor_id,
                    validator=OneOf(EXTRACTOR_TYPES.keys())))
                schema.add(SchemaNode(
                    String(), name='ex_%d_param' % extractor.extractor_id,
                    validator=Length(max=VALUE_LEN)))
                schema.add(SchemaNode(
                    Integer(), name='ex_%d_limit' % extractor.extractor_id,
                    missing=None))
                defaults['ex_%d_files' % extractor.extractor_id] = \
                    extractor.indexed_files
                defaults['ex_%d_type' % extractor.extractor_id] = \
                    extractor.extractor_type
                defaults['ex_%d_param' % extractor.extractor_id] = \
                    extractor.parameter
                defaults['ex_%d_limit' % extractor.extractor_id] = \
                    extractor.limit
        if self._request.params.get('ex_type'):
            schema.add(SchemaNode(
                String(), name='ex_files',
                validator=Length(max=PATTERN_LEN)))
            schema.add(SchemaNode(
                String(), name='ex_type',
                validator=OneOf(EXTRACTOR_TYPES.keys())))
            schema.add(SchemaNode(
                String(), name='ex_param',
                validator=Length(max=VALUE_LEN)))
            schema.add(SchemaNode(
                Integer(), name='ex_limit', missing=None))

        # Values
        if indexer is not None and indexer.value_type == 'select':
            for value in indexer.values:
                schema.add(SchemaNode(
                    String(), name='val_%d_label' % value.value_id,
                    validator=Length(max=VALUE_LEN)))
                schema.add(SchemaNode(
                    String(), name='val_%d_value' % value.value_id,
                    validator=Length(max=VALUE_LEN), missing=None))
                defaults['val_%d_label' % value.value_id] = value.label
                defaults['val_%d_value' % value.value_id] = value.value
            if self._request.params.get('val_label'):
                schema.add(SchemaNode(
                    String(), name='val_label',
                    validator=Length(max=VALUE_LEN)))
                schema.add(SchemaNode(
                    String(), name='val_value',
                    validator=Length(max=VALUE_LEN), missing=None))

        return (
            Form(self._request, schema=schema, defaults=defaults, obj=indexer),
            TabSet(self._request, INDEXER_SETTINGS_TABS))

    # -------------------------------------------------------------------------
    def _create(self, labels, values):
        """Create an indexer.

        :param labels: (dictionary)
            Label in several languages.
        :param values: (dictionary)
            Form values.
        :return: (:class:`~..models.indexers.Indexer` instance or ``None``)
        """
        # Check existence
        indexer_id = make_id(values['indexer_id'], 'token', ID_LEN)
        indexer = DBSession.query(Indexer).filter_by(
            indexer_id=indexer_id).first()
        if indexer is not None:
            self._request.session.flash(
                _('This indexer already exists.'), 'alert')
            return

        # Create indexer
        indexer = Indexer(
            indexer_id, self._label_dict(labels, values), values['value_type'])
        DBSession.add(indexer)
        DBSession.commit()

        return indexer

    # -------------------------------------------------------------------------
    def _save(self, labels, indexer, values):
        """Save an indexer.

        :param labels: (dictionary)
            Label in several languages.
        :param indexer: (:class:`~..models.indexers.Indexer` instance)
            Indexer to save.
        :param values: (dictionary)
            Form values.
        :return: (boolean)
        """
        indexer.labels = dumps(self._label_dict(labels, values))

        # Extractors
        for extractor in indexer.extractors:
            extractor.indexer_files = \
                values['ex_%d_files' % extractor.extractor_id]
            extractor.extractor_type = \
                values['ex_%d_type' % extractor.extractor_id]
            extractor.parameter = \
                values['ex_%d_param' % extractor.extractor_id]
            extractor.limit = \
                values['ex_%d_limit' % extractor.extractor_id]
        if values.get('ex_type'):
            indexer.extractors.append(IndexerExtractor(
                values['ex_files'], values['ex_type'], values['ex_param'],
                values['ex_limit']))

        # Values
        for value in indexer.values:
            value.label = \
                normalize_spaces(values['val_%d_label' % value.value_id])
            value.value = values['val_%d_value' % value.value_id] and \
                normalize_spaces(values['val_%d_value' % value.value_id]) \
                or value.label
        if values.get('val_label'):
            indexer.values.append(IndexerValue(
                values['val_label'], values['val_value']))

        DBSession.commit()
        return True

    # -------------------------------------------------------------------------
    @classmethod
    def _label_dict(cls, langs, values):
        """Return a label dictionary with language as key.

        :param langs: (list)
            Languages to select.
        :param values: (dictionary)
            Form values.
        :return: (dictionay)
        """
        labels = {}
        for lang in langs:
            if values.get('label_%s' % lang):
                labels[lang] = values['label_%s' % lang].encode('utf8')
        return labels
