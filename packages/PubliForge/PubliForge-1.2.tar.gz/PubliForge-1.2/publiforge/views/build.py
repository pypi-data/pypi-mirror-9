# $Id: build.py 7981fd623a54 2015/02/21 08:15:22 Patrick $
"""Build view callables."""

from datetime import timedelta
from time import time
from os.path import join, isdir, dirname, basename, commonprefix, relpath
from math import sqrt
from lxml import etree
from sqlalchemy.exc import IntegrityError
import zipfile
import tempfile
import re

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.response import Response
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.i18n import get_localizer

from ..lib.utils import _, normalize_name, camel_case, export_file_set, age
from ..lib.xml import PUBLIFORGE_RNG_VERSION
from ..lib.viewutils import get_action, current_storage, current_project
from ..lib.viewutils import current_processing, file_download, file_upload
from ..lib.viewutils import variable_schema, variable_input
from ..lib.viewutils import variable_description
from ..lib.form import Form
from ..models import DESCRIPTION_LEN, DBSession, close_dbsession
from ..models.users import User
from ..models.processings import Processing, ProcessingUserVariable
from ..models.packs import FILE_TYPE_MARKS, Pack

STATUS_LABELS = {
    'none': _('In progress...'), 'stop': _('Stopped'), 'end': _('Completed'),
    'fatal': _('In error')}


# =============================================================================
class BuildView(object):
    """Class to manage builds."""

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        request.add_finished_callback(close_dbsession)
        self._request = request

    # -------------------------------------------------------------------------
    @view_config(
        route_name='build_launch', renderer='../Templates/bld_launch.pt')
    def launch(self):
        """Launch one or more builds."""
        # Processing
        project = current_project(self._request)
        processing, processor, output = current_processing(self._request)

        # Packs
        pack_ids = self._request.matchdict.get('pack_ids').split('_')
        packs = DBSession.query(Pack)\
            .filter_by(project_id=project['project_id'])\
            .filter(Pack.pack_id.in_(pack_ids)).all()
        if packs is None:
            raise HTTPNotFound(comment=_('No pack to build!'))

        # Form, action & visible variables with help
        form, groups, variable_values = self._build_form(processing, processor)
        action, description = self._action(
            form, processing, processor, variable_values)
        if self._request.is_xhr:
            return Response(description, content_type='text/html')

        # Launch builds
        build_ids = self._launch_builds(
            form, processing, processor, variable_values, packs)
        if len(build_ids) == 1:
            if self._request.current_route_path() == \
                    self._request.breadcrumbs.current_path():
                self._request.breadcrumbs.pop()
            return HTTPFound(self._request.route_path(
                'build_progress', build_id=build_ids[0]))
        elif len(build_ids) > 1:
            if self._request.current_route_path() == \
                    self._request.breadcrumbs.current_path():
                self._request.breadcrumbs.pop()
            return HTTPFound(self._request.route_path(
                'build_results', project_id=project['project_id']))

        self._request.breadcrumbs.add(_('Build'))
        return {
            'form': form, 'action': action, 'project': project,
            'processing': processing, 'processor': processor, 'groups': groups,
            'variables': variable_values, 'description': description,
            'packs': packs, 'output': output,
            'FILE_TYPE_MARKS': FILE_TYPE_MARKS,
            'variable_input': variable_input}

    # -------------------------------------------------------------------------
    @view_config(
        route_name='build_view', renderer='../Templates/bld_view.pt')
    def view(self):
        """Display a build, eventually, with its result."""
        # Build and project
        build, processing, processor, pack = self._current_build(True)
        project = current_project(
            self._request, int(build['build_id'].split('-')[0]))

        # Working?
        result = self._request.registry['fbuild'].progress(
            self._request, (build['build_id'],))[0]
        if result:
            return HTTPFound(self._request.route_path(
                'build_progress', build_id=build['build_id']))

        # Form & visible variables
        form, groups, variable_values = self._build_form(processing, processor)

        # Action
        action, description = self._action(
            form, processing, processor, variable_values)
        if self._request.is_xhr:
            return Response(description, content_type='text/html')
        if action == 'exp!' and form.validate():
            return self._export_build(
                project, processing, processor, pack, form.values)

        # Launch build
        build_ids = self._launch_builds(
            form, processing, processor, variable_values, (pack,))
        if build_ids:
            return HTTPFound(self._request.route_path(
                'build_progress', build_id=build_ids[0]))

        # Result
        result = self._request.registry['fbuild'].result(build['build_id'])
        log = '\n'.join([
            '[%-7s] %s' % (k[1], k[3]) for k in result.get('log', [])])
        # for k in result.get('log', []):
        #     print '%03d%% [%-7s] %s' % (k[2], k[1], k[3])

        self._request.breadcrumbs.add(
            _('Build'), replace=self._request.route_path(
                'build_progress', build_id=build['build_id']))
        return {
            'form': form, 'action': action, 'project': project,
            'processing': processing, 'processor': processor, 'groups': groups,
            'variables': variable_values, 'description': description,
            'pack': pack, 'output': build['output'],
            'FILE_TYPE_MARKS': FILE_TYPE_MARKS, 'build': build,
            'result': result, 'message': result.get('message'), 'log': log,
            'variable_input': variable_input}

    # -------------------------------------------------------------------------
    @view_config(
        route_name='build_progress', renderer='../Templates/bld_progress.pt')
    @view_config(route_name='build_progress', renderer='json', xhr=True)
    def progress(self):
        """Display the build progress."""
        # Working?
        build = self._current_build()[0]
        build_id = build['build_id']
        working, prgrss = self._request.registry['fbuild'].progress(
            self._request, (build_id,))
        playing = str(
            timedelta(seconds=time() - prgrss[build_id][3])).split('.')[0]
        refresh = self._refresh([prgrss[build_id][3]])

        # Response
        if self._request.is_xhr:
            return {
                'working': working, 'percent': prgrss[build_id][1],
                'message': prgrss[build_id][2].partition('\n')[0],
                'agent': prgrss[build_id][4], 'playing': playing,
                'refresh': refresh}
        if not working:
            return HTTPFound(self._request.route_path(
                'build_view', build_id=build_id, _anchor='build'))
        if 'ajax' not in self._request.params \
           and 'stp?' not in self._request.params:
            self._request.response.headerlist.append(('Refresh', str(refresh)))

        # Stop?
        is_owner = self._request.registry['fbuild'].is_owner(
            self._request, build_id)
        if 'stp!' in self._request.params and is_owner:
            self._request.registry['fbuild'].stop(self._request, (build_id,))

        # Project
        project = current_project(
            self._request, int(build_id.partition('-')[0]))

        self._request.breadcrumbs.add(_('In progress...'))
        return {
            'form': Form(self._request), 'project': project, 'build': build,
            'is_owner': is_owner, 'progress': prgrss[build_id],
            'agent': prgrss[build_id][4], 'playing': playing,
            'refresh': refresh}

    # -------------------------------------------------------------------------
    @view_config(route_name='build_complete',
                 permission=NO_PERMISSION_REQUIRED)
    def complete(self):
        """Complete a build."""
        build_id = self._request.matchdict['build_id']
        key = self._request.matchdict['key']

        made = self._request.registry['fbuild']\
            .complete(self._request, build_id, key)
        return Response('' if made else 'Unable to complete "%s"' % build_id,
                        content_type='text/plain')

    # -------------------------------------------------------------------------
    @view_config(route_name='build_info', renderer='json', xhr=True)
    def info(self):
        """Return information about a build (AJAX)"""
        build_id = self._request.matchdict['build_id']
        result = self._request.registry['fbuild'].result(build_id)
        translate = get_localizer(self._request).translate

        # Working
        if not result:
            working, prgrss = self._request.registry['fbuild'].progress(
                self._request, (build_id,))
            if not working:
                return dict()
            response = {
                'agent': prgrss[build_id][4],
                'playing': str(timedelta(
                    seconds=time() - prgrss[build_id][3])).split('.')[0],
                'message': prgrss[build_id][2].partition('\n')[0]}
        # Not working
        else:
            if len(result['log']) < 13:
                log = ['[%-7s] %s' % (k[1], k[3][:80]) for k in result['log']]
            else:
                log = ['[%-7s] %s' % (k[1], k[3][:80])
                       for k in result['log'][1:4]] + ['[.......] ...'] \
                    + ['[%-7s] %s' % (k[1], k[3][:80])
                       for k in result['log'][-9:]]
            log = '\n'.join(log)
            response = {
                'playing': str(timedelta(
                    seconds=result['log'][-1][0] -
                    result['log'][0][0])).split('.')[0],
                'log': log}
            if 'message' in result:
                response['message'] = translate(result['message'])
            if 'values' in result:
                response['values'] = ' ; '.join(result['values'])
            if 'files' in result:
                response['files'] = ' ; '.join(result['files'])

        response['labels'] = {
            'agent': translate(_('Agent:')),
            'playing': translate(_('Playing time:')),
            'message': translate(_('Message:')),
            'values': translate(_('Values:')),
            'files': translate(_('Files:')),
            'log': translate(_('Log:'))}

        return response

    # -------------------------------------------------------------------------
    @view_config(route_name='build_log')
    def log(self):
        """Download current log."""
        build = self._current_build()[0]
        project = current_project(
            self._request, int(build['build_id'].partition('-')[0]))
        content = self._request.registry['fbuild'].result(build['build_id'])
        content = '\n'.join([
            '[%-7s] %s' % (k[1], k[3]) for k in content.get('log', [])])
        filename = normalize_name('%s-%s.log' % (
            project['label'], build['build_id'].partition('-')[2]))
        response = Response(content, content_type='text/plain')
        response.headerlist.append((
            'Content-Disposition', 'attachment; filename="%s"' % filename))
        return response

    # -------------------------------------------------------------------------
    @view_config(
        route_name='build_results', renderer='../Templates/bld_results.pt')
    @view_config(route_name='build_results', renderer='json', xhr=True)
    def results(self):
        """List all builds in progress or with result."""
        # Action 1
        project = current_project(self._request)
        user_id = project['perm'] != 'leader' \
            and self._request.session['user_id'] or None
        action, items = get_action(self._request)
        if action[0:4] == 'del!':
            self._request.registry['fbuild'].forget_results(
                project['project_id'], user_id, build_ids=items)
        elif action[0:4] == 'stp!':
            self._request.registry['fbuild'].stop(
                self._request, items, user_id)

        # Environment
        working = False
        prgrss = users = processings = packs = None
        refresh = int(self._request.registry.settings.get('refresh.long', 5))
        build_list = self._request.registry['fbuild'].build_list(
            project['project_id'], user_id)

        # Ajax
        if self._request.is_xhr:
            starts = dict([(k['build_id'], k['start']) for k in build_list])
            working, prgrss = self._request.registry['fbuild'].progress(
                self._request, starts.keys())
            prgrss = dict([
                (k, (str(timedelta(seconds=time() - starts[k])).split('.')[0],
                     prgrss[k][1]))
                for k in prgrss])
            refresh = self._refresh(starts.values(), refresh)
            return {'working': working, 'status': prgrss, 'refresh': refresh}

        # Build parameters
        if build_list:
            packs = [k['pack_id'] for k in build_list]
            packs = dict(
                DBSession.query(Pack.pack_id, Pack.label)
                .filter_by(project_id=project['project_id'])
                .filter(Pack.pack_id.in_(packs)).all())
            build_list = [k for k in build_list if k['pack_id'] in packs]
        if build_list:
            processings = [k['processing_id'] for k in build_list]
            processings = DBSession.query(Processing)\
                .filter_by(project_id=project['project_id'])\
                .filter(Processing.processing_id.in_(processings)).all()
            processings = dict([
                (k.processing_id, (k.label, k.output)) for k in processings])
            for k in processings:
                if processings[k][1] and '%(user)s' in processings[k][1]:
                    processings[k] = (
                        processings[k][0], processings[k][1].replace(
                            '%(user)s',
                            camel_case(self._request.session['login'])))
            users = [k['user_id'] for k in build_list]
            users = dict(DBSession.query(User.user_id, User.name)
                         .filter(User.user_id.in_(users)).all())
            working, prgrss = self._request.registry['fbuild'].progress(
                self._request, [k['build_id'] for k in build_list])
            refresh = self._refresh([k['start'] for k in build_list], refresh)

        # Action 2
        if action[0:4] == 'dnl!':
            action = self._download_results(build_list, processings, items)
            if action is not None:
                return action

        # Refresh
        if working and 'ajax' not in self._request.params:
            self._request.response.headerlist.append(
                ('Refresh', str(refresh)))

        self._request.breadcrumbs.add(_('Last results'))
        return {
            'age': age, 'form': Form(self._request), 'action': action,
            'working': working, 'project': project, 'results': build_list,
            'progress': prgrss, 'users': users, 'processings': processings,
            'packs': packs, 'status_labels': STATUS_LABELS, 'refresh': refresh}

    # -------------------------------------------------------------------------
    def _current_build(self, full=False):
        """Initialize ``request.session['build']`` and return it as current
        build dictionary.

        If ``full`` is ``True``, this method also returns
        :class:`~.models.processings.Processing` object, processor
        :class:`lxml.etree.ElementTree` object and :class:`~.models.packs.Pack`
        object.

        :param full: (boolean)
            If ``True``, force database reading and return processing and
            pack objects.
        :return: (tuple)
            A tuple such as ``(build_dictionary, processing_object,
            pack_object)`` or a :class:`pyramid.httpexceptions.`HTTPNotFound`
            exception.

        ``build_dictionary`` has the following keys: ``build_id``,
        ``processing_id``, ``pack_id``, ``pack_label``, ``output``.
        """
        # Already in session
        build_id = self._request.matchdict['build_id']
        if not full and 'build' in self._request.session \
                and self._request.session['build']['build_id'] == build_id:
            return self._request.session['build'], None, None, None

        # Processing & processor
        project_id, processing_id, pack_id = build_id.split('-')[0:3]
        processing, processor, output = \
            current_processing(self._request, project_id, int(processing_id))

        # Pack
        pack = DBSession.query(Pack).filter_by(
            project_id=project_id, pack_id=pack_id).first()
        if pack is None:
            raise HTTPNotFound(comment=_('This pack does not exist!'))

        self._request.session['build'] = {
            'build_id': build_id, 'processing_id': processing.processing_id,
            'pack_id': pack_id, 'pack_label': pack.label, 'output': output}
        return self._request.session['build'], processing, processor, pack

    # -------------------------------------------------------------------------
    def _build_form(self, processing, processor):
        """Return a build form with a validating schema for visible variables.

        :param processing:
            (:class:`~.models.processings.Processing` instance)
        :param processor: (:class:`lxml.etree.ElementTree` instance)
            Processor of current processing.
        :return: (tuple)
            A tuple such as ``(form, groups, variables)``

        ``groups`` is a list of group :class:`lxml.etree.Element` objects
        containing visible variables. ``variables`` is a dictionary of visible
        variables (see :meth:`_variable_values`).
        """
        variable_values = self._variable_values(
            processor, processing.variables, processing.user_variables)
        groups = []
        for group in processor.findall('processor/variables/group'):
            for var in group.findall('var'):
                if var.get('name') in variable_values:
                    groups.append(group)
                    break

        schema, defaults = variable_schema(processor, variable_values, False)
        form = Form(
            self._request, schema=schema, defaults=defaults, obj=processing)
        return form, groups, variable_values

    # -------------------------------------------------------------------------
    def _launch_builds(self, form, processing, processor, variables, packs):
        """Launch builds.

        :param form: (:class:`~.lib.form.Form` instance)
             Build form.
        :param processing:
             (:class:`~.models.processings.Processing` instance)
        :param processor: (:class:`lxml.etree.ElementTree` instance)
            Processor of current processing.
        :param variables: (dictionary)
             Dictionary of variables (see :meth:`_variable_values`).
        :param packs: (list)
             List of :class:`~.models.packs.Pack` objects.
        :return: (list)
             List of launched builds.
        """
        if (len(variables) or 'view' in self._request.current_route_path()) \
                and \
                ('bld!.x' not in self._request.params or not form.validate()):
            return tuple()

        # Save variable modifications
        user_id = self._request.session['user_id']
        DBSession.query(ProcessingUserVariable).filter_by(
            project_id=processing.project_id,
            processing_id=processing.processing_id, user_id=user_id).delete()
        for var in processor.findall('processor/variables/group/var'):
            name = var.get('name')
            if name in form.values:
                default = variables[name][1] == 'true' \
                    if var.get('type') == 'boolean' else variables[name][1]
                if form.values[name] != default:
                    processing.user_variables.append(ProcessingUserVariable(
                        user_id, name, form.values[name]))
        try:
            DBSession.commit()
        except IntegrityError:
            DBSession.rollback()

        # Parallel processor
        if processing.processor.startswith('Parallel'):
            return self._launch_parallel_builds(processing, processor, packs)

        # Create builds and start them
        build_ids = []
        for pack in packs:
            build_id = self._request.registry['fbuild'].start_build(
                self._request, processing, processor, pack)
            if build_id:
                build_ids.append(build_id)

        return build_ids

    # -------------------------------------------------------------------------
    def _launch_parallel_builds(self, processing, processor, packs):
        """Launch builds of a parallel processor.

        :param processing:
             (:class:`~.models.processings.Processing` instance)
        :param processor: (:class:`lxml.etree.ElementTree` instance)
            Processor of current processing.
        :param packs: (list)
             List of :class:`~.models.packs.Pack` objects.
        :return: (list)
             List of launched builds.
        """
        build_ids = []
        done = set()
        processings = dict([
            ('prc%d.%d' % (k.project_id, k.processing_id), k)
            for k in DBSession.query(Processing)
            .filter_by(project_id=processing.project_id)
            if not k.processor.startswith('Parallel')])
        values = dict((k.name, k.value) for k in processing.user_variables
                      if k.user_id == self._request.session['user_id'])
        defaults = dict((k.name, k.default) for k in processing.variables)

        for var in processor.findall('processor/variables/group/var'):
            value = values.get(var.get('name')) \
                or defaults.get(var.get('name'))
            if value not in processings or value in done:
                continue
            current_processor = self._request.registry['fbuild'].processor(
                self._request, processings[value].processor)
            if current_processor is None:
                raise HTTPNotFound(
                    comment=_('Unknown processor "${p}"!',
                              {'p': processings[value].processor}))
            for pack in packs:
                build_id = self._request.registry['fbuild'].start_build(
                    self._request, processings[value], current_processor, pack)
                if build_id:
                    build_ids.append(build_id)
            done.add(value)

        return build_ids

    # -------------------------------------------------------------------------
    def _action(self, form, processing, processor, variable_values):
        """Return current action and a description text.

        :param form: (:class:`~.lib.form.Form` instance)
            Current form.
        :param processing: (:class:`~.models.processings.Processing` instance)
            Current processing object.
        :param processor: (:class:`lxml.etree.ElementTree` instance)
            Processor of current processing.
        :param variable_values: (dictionary)
            Values affected to the variables of current processing.
        :return: (tuple)
            A tuple such as ``(action, description)``.
        """
        description = None
        action = get_action(self._request)[0]

        if action[0:4] == 'des!':
            description = variable_description(
                self._request, processor.find('processor'),
                action[4:], variable_values, False, True)
        elif action[0:4] == 'rst!':
            name = action[4:]
            var = processor.xpath(
                'processor/variables/group/var[@name="%s"]' % name)
            if len(var) == 1 and name in variable_values:
                form.values[name] = (variable_values[name][1] == 'true') \
                    if var[0].get('type') == 'boolean' \
                    else variable_values[name][1]
                form.static(name)
        elif action[0:4] == 'upl!':
            message = \
                self._request.params.get('message', '')[0:DESCRIPTION_LEN] \
                or get_localizer(self._request)\
                .translate(_('Updated before "${p}"', {'p': processing.label}))
            file_upload(self._request, action[4:], message)
            action = ''

        return action, description

    # -------------------------------------------------------------------------
    def _export_build(self, project, processing, processor, pack, values):
        """Export build.

        :param project: (dictionary)
            Project dictionary.
        :param processing:
            (:class:`~.models.processings.Processing` instance)
        :param processor: (:class:`lxml.etree.ElementTree` instance)
            Processor of current processing.
        :param pack: (:class:`~.models.packs.Pack` instance)
        :param values: (dictionary)
            Variables values.
       :return: (:class:`pyramid.response.Response` instance)
        """
        # Header
        settings = self._request.registry.settings
        root = etree.Element('publiforge', version=PUBLIFORGE_RNG_VERSION)
        build_elt = etree.SubElement(root, 'build')
        build_elt.set(
            'id', '%s_%d-%d-%d' % (settings['uid'], project['project_id'],
                                   processing.processing_id, pack.pack_id))

        # Settings
        build_elt.append(etree.Comment('=' * 68))
        group_elt = etree.SubElement(build_elt, 'settings')
        etree.SubElement(group_elt, 'setting', key='storage.root')\
            .text = '../../Storages~'
        etree.SubElement(group_elt, 'setting', key='build.root')\
            .text = '../../Builds~'
        etree.SubElement(group_elt, 'setting', key='build.develop')\
            .text = settings.get('build.develop', 'true')
        etree.SubElement(group_elt, 'setting', key='processor.roots')\
            .text = '../../Processors'

        # Processing
        build_elt.append(etree.Comment('=' * 68))
        group_elt = etree.SubElement(build_elt, 'processing')
        etree.SubElement(group_elt, 'processor').text = processing.processor
        processing.export_user_variables(group_elt, processor, values)
        export_file_set(group_elt, processing, 'resource')
        export_file_set(group_elt, processing, 'template')

        # Pack
        build_elt.append(etree.Comment('=' * 68))
        group_elt = etree.SubElement(build_elt, 'pack')
        if pack.recursive:
            group_elt.set('recursive', 'true')
        export_file_set(group_elt, pack, 'file')
        export_file_set(group_elt, pack, 'resource')
        export_file_set(group_elt, pack, 'template')

        # Response
        filename = normalize_name('%s-%d-%d.pfbld.xml' % (
            project['label'], processing.processing_id, pack.pack_id))
        xml = etree.tostring(
            root, pretty_print=True, encoding='utf-8', xml_declaration=True)
        xml = re.sub(r'\s*<(/?)value>\s*', '<\\1value>', xml)
        response = Response(xml, content_type='application/xml')
        response.headerlist.append((
            'Content-Disposition', 'attachment; filename="%s"' % filename))
        return response

    # -------------------------------------------------------------------------
    def _variable_values(self, processor, variables, user_variables):
        """Return a dictionary of variable values.

        :param processor: (:class:`lxml.etree.ElementTree` instance)
            Processor of current processing.
        :param variables: (:class:`~.models.processings.ProcessingVariable`)
            Variables of current processing.
        :param user_variables:
            (:class:`~.models.processings.ProcessingUserVariable`)
            Variables of current processing.
        :return: (dictionay)
            A dictionary such as {<name>: (<value>, <default>, <label>),...}.
        """
        user_id = self._request.session['user_id']
        variables = dict([(k.name, k) for k in variables])
        user_variables = dict([
            (k.name, k) for k in user_variables if k.user_id == user_id])
        values = {}

        for var in processor.findall('processor/variables/group/var'):
            name = var.get('name')
            if not (variables[name].visible if name in variables and
                    variables[name].visible is not None
                    else bool(var.get('visible'))):
                continue
            default = variables[name].default if name in variables \
                and variables[name].default is not None \
                else var.findtext('default')
            value = user_variables[name].value if name in user_variables \
                else default
            label = None
            if value is not None and var.get('type') == 'select':
                label = dict([
                    (k.get('value', k.text), k.text)
                    for k in var.findall('option')]).get(value, value)
            values[name] = (value, default, label)

        return values

    # -------------------------------------------------------------------------
    def _download_results(self, build_list, processings, build_ids):
        """Gather results in a ZIP file and return a Pyramid response.

        :param build_list: (list)
            List of builds of current project.
        :param processings: (dictionary)
            Dictionary of used processings.
        :param build_ids: (list)
            List of build IDs to download.
        :return: (:class:`pyramid.response.Response` instance or raise a
            :class:`pyramid.httpexceptions.HTTPNotFound` exception.)
        """
        # Create file list
        filenames = []
        for build in build_list:
            if build['build_id'] in build_ids and build.get('files'):
                path = processings[build['processing_id']][1]
                if current_storage(self._request, path.partition('/')[0]):
                    filenames += [join(path, k) for k in build['files']]

        # Empty list
        if not filenames:
            self._request.session.flash(_('No result to download!'), 'alert')
            return

        # Single file
        storage_root = self._request.registry.settings['storage.root']
        if len(filenames) == 1:
            return file_download(
                self._request, storage_root, filenames, basename(filenames[0]))

        # Several files
        tmp = tempfile.NamedTemporaryFile(
            dir=self._request.registry.settings['temporary_dir'])
        zip_file = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
        root = join(storage_root, commonprefix(filenames))
        if not isdir(root):
            root = dirname(root)
        for name in filenames:
            name = join(storage_root, name)
            zip_file.write(name, relpath(name, root))
        zip_file.close()
        return file_download(self._request, '', (tmp.name,), 'results.zip')

    # -------------------------------------------------------------------------
    def _refresh(self, start_times, initial=None):
        """Compute the best delay to refresh a page.

        :param start_times: (list)
            List of starting time of each build.
        :param initial: (integer, default=refresh.short of settings)
            Initial delay in seconds.
        :return: (integer)
            Delay in seconds.
        """
        initial = initial or \
            int(self._request.registry.settings.get('refresh.short', 2))
        return not start_times and initial or min(
            int(((3 + sqrt(1 + time() - max(start_times))) / 4) * initial), 15)
