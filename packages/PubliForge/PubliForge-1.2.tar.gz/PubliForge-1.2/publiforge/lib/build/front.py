# $Id: front.py 7981fd623a54 2015/02/21 08:15:22 Patrick $
"""Front build management.

A *front* is a web site.
"""

import logging
import xmlrpclib
from time import time, sleep
from datetime import datetime
from random import randint
from threading import Thread
from os import walk, makedirs, rename
from os.path import join, exists, isfile, dirname, relpath, normpath
from cStringIO import StringIO
from lxml import etree
import re

from pyramid.i18n import get_localizer
from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden

from ..utils import _, localizer, copy_content, decrypt
from ..utils import camel_case, has_permission, EXCLUDED_FILES
from ..viewutils import current_storage
from ..packutils import pack2task
from ..rsync import get_block_size, SigFile, PatchedFile, DeltaFile
from ...views import xmlrpc
from ...models import DBSession
from ...models.users import User
from ...models.processors import Processor
from ...models.storages import StorageUser
from ...models.processings import ADD2PACK_TARGETS
from ...models.packs import Pack, PackFile


LOG = logging.getLogger(__name__)


# =============================================================================
class FrontBuildManager(object):
    """This class manages front builds.

    One instance of :class:`FrontBuildManager` is created during application
    initialization. It is only used in front mode. It is stored in application
    registry.

    ``self._agents`` is a dictionary such as ``{url: (agent_id, password,
    weight, processor_list, processor_expire_time, concurrent),... }`` which
    stores agent features.

    ``self._builds`` is a dictionary of :class:`FrontBuild` objects.

    ``self._results`` is a dictionary of dictionaries such as ``{build_id:
    result_dict}``. ``result_dict`` is a dictionary with following keys:
    ``status``, ``log``, ``expire``, ``project_id``, ``user_id``. According to
    build events, it can also contains ``files``, ``values`` and ``error``
    keys.

    ``self._results[build_id]['status']`` is one of the following strings:
    ``stop``, ``fatal`` or ``end``.

    ``self._results[build_id]['log']`` is a list of tuples such as
    ``(timestamp, step, percent, message)``.
    """
    # pylint: disable = locally-disabled, R0902

    # -------------------------------------------------------------------------
    def __init__(self, settings):
        """Constructor method.

        :param settings: (dictionary)
            Setting dictionary.
        """
        # Attributes
        self.storage_root = settings['storage.root']
        self.build_ttl = int(settings.get('build.ttl', 1800))
        self.result_ttl = int(settings.get('build.result_ttl', 604800))
        self._concurrent = [int(settings.get('front.synchronize', 1)), 1]
        self._refresh = int(settings.get('agent.refresh', 0))
        self._builds = {}
        self._results = {}

        # Agent list
        self._agents = {}
        for index in range(0, 100):
            pfx = 'agent.%d' % index
            weight = int(settings.get('%s.weight' % pfx, 0))
            if weight:
                self._agents[settings.get('%s.url' % pfx, '')] = [
                    None, settings.get('%s.password' % pfx, ''),
                    weight, None, 0, 0]

    # -------------------------------------------------------------------------
    def agent_urls(self):
        """Return a list of URLs of available agents."""
        return [k or 'localhost' for k in self._agents.keys()]

    # -------------------------------------------------------------------------
    def refresh_agent_list(self, request):
        """Refresh processor list for each agent.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        """
        # Refresh processor list
        now = time()
        modified = False
        self._concurrent[1] = 0
        for url in self._agents:
            if self._agents[url][0] is None or \
                    (self._agents[url][0] == '?' and
                     self._refresh and self._agents[url][4] < now):
                error, agent_id = self.call(request, url, 'agent_id')
                self._agents[url][0] = agent_id or '?'
            if self._agents[url][3] is None \
               or (self._refresh and self._agents[url][4] < now):
                error, processors = self.call(request, url, 'processor_list')
                if error:
                    LOG.error('%s: %s', url, error)
                processors = processors or (tuple(), 0)
                self._agents[url][3] = processors[0]
                self._agents[url][4] = now + self._refresh
                self._agents[url][5] = processors[1]
                modified = True
            self._concurrent[1] += self._agents[url][5]
        if not modified:
            return

        # Refresh processor records
        if self._refresh:
            DBSession.query(Processor).filter(
                Processor.updated + self._refresh < now).delete()
            DBSession.commit()
        processors = [k[0] for k in DBSession.query(Processor.processor_id)]
        for url in sorted(self._agents):
            for processor_id in self._agents[url][3]:
                if processor_id in processors:
                    continue
                error, xml = self.call(
                    request, url, 'processor_xml', processor_id)
                if error:
                    LOG.error('%s: %s', url, error)
                    continue
                processor = Processor.load(processor_id, xml)
                if isinstance(processor, basestring):
                    LOG.error('%s: %s', url,
                              get_localizer(request).translate(processor))
                    continue
                DBSession.add(processor)
                DBSession.commit()

    # -------------------------------------------------------------------------
    def find_agent(self, request, processor_id):
        """Find an agent which serves ``processor_id``.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param processor_id: (string)
            ID of the processor agent must serve.
        :return: (tuple):
            A tuple such as ``(url, uid)`` or (``None``, ``None``).
        """
        found_url = None
        agent_id = ''
        min_activity = 0
        self.refresh_agent_list(request)
        for url in self._agents:
            if self._agents[url][3] and processor_id in self._agents[url][3]:
                error, activity = self.call(request, url, 'activity')
                if error:
                    LOG.error('%s: %s', url, error)
                    continue
                if activity == -1:
                    continue
                activity = (activity + .1) / self._agents[url][2]
                if found_url is None or activity < min_activity:
                    found_url = url
                    agent_id = self._agents[url][0]
                    min_activity = activity
        return found_url, agent_id

    # -------------------------------------------------------------------------
    def processor(self, request, processor_id):
        """Return a processor tree.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param processor_id: (string)
            Processor ID
        :return: (:class:`lxml.etree.ElementTree` or ``None``)
        """
        self.refresh_agent_list(request)
        xml = DBSession.query(Processor.xml).filter_by(
            processor_id=processor_id).first()
        if xml is not None:
            return etree.parse(StringIO(xml[0].encode('utf8')))

    # -------------------------------------------------------------------------
    def start_build(self, request, processing, processor, pack, tasks=None):
        """Find an agent, convert processing and pack into dictionaries,
        create a build, add it in ``self._builds`` dictionary and try to start
        it.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param processing:
            (:class:`~.models.processings.Processing` instance)
            Processing object.
        :param processor: (:class:`lxml.etree.ElementTree` instance)
            Processor of current processing.
        :param pack: (:class:`~.models.projects.ProjectPack` instance)
            Pack object.
        :param tasks: (tuple, optional)
            A tuple such as ``(task_ko, task_ok)``. If it is not ``None``,
            the pack is transfered to the task according to success.
        :return: (string or ``None``)
            Build ID.
        """
        # Compute ID
        self._cleanup()
        user_id = request.session['user_id']
        build_id = '{prj_id}-{prc_id}-{pck_id}-{usr_id}'.format(
            prj_id=processing.project_id, prc_id=processing.processing_id,
            pck_id=pack.pack_id, usr_id=user_id)
        if build_id in self._builds:
            request.session.flash(_(
                '${i}: action already in progress.', {'i': build_id}), 'alert')
            return build_id

        # Processing dictionary
        processing_dict = {
            'processor_id': processing.processor,
            'variables': self._variables2dict(request, processing, processor),
            'resources': self._file_set2list(request, processing, 'resource'),
            'templates': self._file_set2list(request, processing, 'template'),
            'output': processing.output or '',
            'add2pack': processing.add2pack or ''}
        if request.session.peek_flash('alert'):
            return
        if processing_dict['output'] \
                and '%(user)s' in processing_dict['output']:
            processing_dict['output'] = processing_dict['output'].replace(
                '%(user)s', camel_case(request.session['login']))

        # Pack dictionary
        pack_dict = {
            'project_id': pack.project_id, 'pack_id': pack.pack_id,
            'label': pack.label, 'recursive': pack.recursive,
            'files': self._file_set2list(request, pack, 'file'),
            'resources': self._file_set2list(request, pack, 'resource'),
            'templates': self._file_set2list(request, pack, 'template'),
            'task_ko': tasks and tasks[0] or '',
            'task_ok': tasks and tasks[1] or ''}
        if request.session.peek_flash('alert'):
            return

        # Create a FrontBuild object
        if build_id in self._results:
            del self._results[build_id]
        self._builds[build_id] = FrontBuild(
            self, build_id, user_id, request.session['lang'], processing_dict,
            pack_dict)
        self.start_waiting(request)
        return build_id

    # -------------------------------------------------------------------------
    def start_waiting(self, request):
        """Start waiting builds.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        """
        # Look for waiting builds
        waiting = []
        synchronizing = 0
        running = 0
        for build_id in self._builds:
            if self._builds[build_id].result['log'][0][1] == 'wait':
                waiting.append(build_id)
            elif self._builds[build_id].result['log'][-1][1] == 'sync':
                synchronizing += 1
                running += 1
            elif not self._builds[build_id].stopped():
                running += 1
        if not waiting or synchronizing >= self._concurrent[0] \
           or running >= self._concurrent[1]:
            return

        # Start waiting builds
        waiting = sorted(
            waiting,
            key=lambda build_id: self._builds[build_id].result['log'][0][0])
        for build_id in waiting:
            self._builds[build_id].expire = time() + self.build_ttl
            if synchronizing < self._concurrent[0] \
               and running < self._concurrent[1] \
               and self._builds[build_id].start(request):
                running += 1
                if self._builds[build_id].agent_url:
                    synchronizing += 1
                sleep(.2)

    # -------------------------------------------------------------------------
    def progress(self, request, build_ids):
        """Return the progress of builds.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param build_ids: (list)
            Build ID list.
        :return: (tuple)
            Return a tuple such as ``(<working>, <progress_dictionary>)``.

        ``<working>`` is a boolean indicating whether one of the processing is
        in progress.

        ``<progress_dictionary>`` is a dictionary such as ``{<build_id>:
        (<step>, <percent>, <message>, <start_time>, <agent_id)>),...}``
        where ``<step>`` is one of the following:

        * ``wait``: waiting
        * ``start``: starting
        * ``sync``: synchronizing storages between front and agent
        * ``a_???``: an :class:`~.lib.build.agent.AgentBuildManager` step
        * ``get``: getting result
        * ``warn``: a warning occurred
        * ``error``: an error occurred
        * ``fatal``: a fatal error occurred
        * ``stop``: stopping
        * ``end``: successfully completed
        * ``none``: unknown or not in progress build
        """
        self._cleanup()
        self.start_waiting(request)
        working = False
        prgrss = {}
        for build_id in build_ids:
            if build_id in self._builds:
                prgrss[build_id] = self._builds[build_id].progress(request)
                working = True
            else:
                prgrss[build_id] = ('none', 0, '', time(), '')
        return working, prgrss

    # -------------------------------------------------------------------------
    def complete(self, request, build_id, key):
        """Get the result and eventually download the output directory in
        storage.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param build_id: (string)
            Build ID.
        :param key: (string)
            Key to authenticate the request.
        :return: (boolean)
        """
        if build_id in self._builds:
            completed = self._builds[build_id].complete(request, key)
        else:
            completed = build_id in self._results
        self._cleanup()
        self.start_waiting(request)
        return completed

    # -------------------------------------------------------------------------
    def stop(self, request, build_ids, user_id=None):
        """Stop a build.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param build_ids: (list, optional)
            IDs of build to stop.
        :param user_id: (integer, optional)
            Current user ID.
        """
        self._cleanup()
        for build_id in build_ids:
            if build_id in self._builds \
               and self.is_owner(request, build_id, user_id):
                self._builds[build_id].stop(request)

    # -------------------------------------------------------------------------
    def result(self, build_id):
        """Return the result of a build.

        :param build_id: (string)
            Build ID.
        :return: (dictionary)
        """
        self._cleanup()
        return self._results.get(build_id, {})

    # -------------------------------------------------------------------------
    def forget_results(self, project_id, user_id=None, build_ids=None,
                       pack_id=None):
        """Forget results for one pack or several builds.

        :param project_id: (integer)
            Project ID.
        :param user_id: (integer, optional)
            Current user ID.
        :param build_ids: (list, optional)
            IDs of build to forget.
        :param pack_id: (string, optional)
            Pack ID.
        """
        for build_id, result in self._results.items():
            if project_id == result['project_id'] \
                    and (user_id is None or user_id == result['user_id']) \
                    and ((build_ids is None and pack_id is None) or
                         (build_ids is not None and build_id in build_ids) or
                         pack_id == int(build_id.split('-')[2])):
                del self._results[build_id]

    # -------------------------------------------------------------------------
    def build_list(self, project_id, user_id=None):
        """List all builds of a project.

        :param project_id: (integer)
            Project ID.
        :param user_id: (integer, optional)
            User ID.
        :return: (list)
            A list of dictionaries.

        Returned dictionaries are sorted by start time. Each dictionary has
        following keys: ``build_id``, ``start``, ``status``, ``processing_id``,
        ``pack_id``, ``user_id``.
        """
        self._cleanup()
        builds = []
        for build_id, build in self._builds.items():
            if build.result['project_id'] == project_id and \
                    (user_id is None or build.result['user_id'] == user_id):
                builds.append({
                    'build_id': build_id, 'start': build.result['log'][0][0],
                    'status': build.result['status'],
                    'processing_id': int(build_id.split('-')[1]),
                    'pack_id': int(build_id.split('-')[2]),
                    'user_id': build.result['user_id']})

        for build_id, result in self._results.items():
            if result['project_id'] == project_id \
                    and (user_id is None or result['user_id'] == user_id):
                builds.append({
                    'build_id': build_id, 'start': result['log'][0][0],
                    'status': result['status'],
                    'processing_id': int(build_id.split('-')[1]),
                    'pack_id': int(build_id.split('-')[2]),
                    'user_id': result['user_id'],
                    'files': 'files' in result and result['files'] or None})

        return sorted(builds, key=lambda k: k['start'], reverse=True)

    # -------------------------------------------------------------------------
    def is_owner(self, request, build_id, user_id=None):
        """Check if user ``user_id`` has launched the build ``build_id``.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param build_id: (string)
            Build to check
        :param user_id: (integer, optional)
            User ID to check. By default, the current user is checked.
        :rtype: (boolean)
        """
        if user_id is None:
            user_id = request.session['user_id']
        if (build_id in self._results and
                self._results[build_id]['user_id'] == user_id) or \
                (build_id in self._builds and
                 self._builds[build_id].result['user_id'] == user_id) or \
                has_permission(request, 'prj_manager'):
            return True
        return False

    # -------------------------------------------------------------------------
    def call(self, request, url, method, *args):
        """Call an agent method directly or via RPC.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param url: (string)
            The agent URL or ``localhost`` to call without RPC.
        :param method: (string)
            Method to call
        :param args:
            Non-keyworded arguments for method.
        :return: (tuple)
            A tuple such as ``(<error>, <result>)`` where ``<error>`` is a
            string and ``<result>`` depends on ``method``.

        In addition to the required arguments, this method sends also a context
        dictionary with ``lang`` (language for error messages), ``front_id``,
        ``password`` (to authenticate front), ``user_id`` and ``local``
        (``True`` if called without XML-RPC). If this method is called for a
        local agent, it adds a ``request`` key in context.
        """
        # Create context
        context = {'front_id': request.registry.settings['uid'],
                   'password': self._agents[url][1],
                   'user_id': request.session['user_id'],
                   'login': request.session['login'],
                   'lang': request.session['lang'],
                   'name': request.session['name']}

        # Local agent
        if not url:
            context['local'] = True
            context['request'] = request
            try:
                return getattr(xmlrpc, method)(request, context, *args)
            except AttributeError as err:
                return err, None

        # Remote agent
        context['local'] = False
        proxy = xmlrpclib.ServerProxy('%s/xmlrpc' % url, verbose=False)
        try:
            error, result = getattr(proxy, method)(context, *args)
        except IOError as err:
            error, result = err.strerror, None
        except (OverflowError, MemoryError) as err:
            error, result = err, None
        except xmlrpclib.ProtocolError as err:
            error, result = err.errmsg, None
        except xmlrpclib.Fault as err:
            error, result = err.faultString, None
        return error, result

    # -------------------------------------------------------------------------
    def _cleanup(self):
        """Delete completed builds and expired results and kill long builds."""
        # Build -> result or stop
        now = time()
        for build_id in self._builds.keys():
            if self._builds[build_id].stopped():
                self._results[build_id] = self._builds[build_id].result
                self._results[build_id]['expire'] = now + self.result_ttl
                del self._builds[build_id]
            elif self._builds[build_id].expire < now:
                self._builds[build_id].stopped(_('timeout'))

        # Remove old results
        for build_id in self._results.keys():
            if self._results[build_id]['expire'] < now:
                del self._results[build_id]

    # -------------------------------------------------------------------------
    @classmethod
    def _variables2dict(cls, request, processing, processor):
        """Create a variable dictionary from a processing record and its
        processor.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param processing:
            (:class:`~.models.processings.Processing` instance)
        :param processor: (:class:`lxml.etree.ElementTree` instance)
            Processor of current processing.
        :return: (dictionary)
        """
        defaults = dict([(k.name, k.default) for k in processing.variables])
        values = dict([(k.name, k.value) for k in processing.user_variables
                       if k.user_id == request.session['user_id']])
        variables = {}
        for var in processor.findall('processor/variables/group/var'):
            name = var.get('name')
            value = values[name] if name in values \
                else (defaults[name] if name in defaults and
                      defaults[name] is not None
                      else var.findtext('default', ''))
            if var.get('type') in ('string', 'text'):
                variables[name] = value
            elif var.get('type') == 'boolean':
                variables[name] = (value == 'true')
            elif var.get('type') == 'integer':
                variables[name] = int(value)
            elif var.get('type') == 'select':
                if value not in [k.get('value') or k.text
                                 for k in var.findall('option')]:
                    request.session.flash(
                        _('${v}: bad value.', {'v': name}), 'alert')
                    LOG.error(get_localizer(request).translate(
                        _('${v}: bad value.', {'v': name})))
                    return variables
                variables[name] = int(value) if value.isdigit() else value
            elif var.get('type') == 'regex':
                if not re.match(var.find('pattern').text, value):
                    request.session.flash(
                        _('${v}: bad value.', {'v': name}), 'alert')
                    LOG.error(get_localizer(request).translate(
                        _('${v}: bad value.', {'v': name})))
                    return variables
                variables[name] = value
        return variables

    # -------------------------------------------------------------------------
    @classmethod
    def _file_set2list(cls, request, record, file_type):
        """Save set of files in a list.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param record: (:class:`~.models.processings.Processing`
            or :class:`~.models.projects.ProjectPack` instance).
        :param file_type: ('file', 'resource' or 'template')
            File type.
        """
        file_set = []
        items = [k for k in record.files if k.file_type == file_type]
        if len(items) == 0:
            return file_set

        storage_root = request.registry.settings['storage.root']
        for item in sorted(items, key=lambda k: k.sort):
            if not exists(join(storage_root, item.path)):
                request.session.flash(
                    _('"${n}" does not exist.', {'n': item.path}), 'alert')
                LOG.error(get_localizer(request).translate(
                    _('"${n}" does not exist.', {'n': item.path})))
                return
            if file_type in ('file', 'resource'):
                file_set.append(item.path)
            else:
                file_set.append((item.path, item.target))

        return file_set


# =============================================================================
class FrontBuild(object):
    """This class manages a build locally and via an agent.

    ``self.result`` is a dictionary with following keys: ``status``, ``log``,
    ``start``, ``expire``, ``project_id``, ``user_id``. At the process end, it
    can also have ``files``, ``values``, ``error`` and ``end`` keys.

    ``self.result['log']`` is a list of tuples such as ``(timestamp, step,
    percent, message)``.

    ``self.result['expire']`` is the date beyond which the build is destroyed.

    ``self.key`` is a key to authenticate transaction between front and
    agent.
    """
    # pylint: disable = locally-disabled, R0902, R0913

    # -------------------------------------------------------------------------
    def __init__(self, build_manager, build_id, user_id, lang, processing,
                 pack):
        """Constructor method.

        :param build_manager: (:class:`FrontBuildManager` instance)
            Application :class:`FrontBuildManager` object.
        :param build_id: (string)
            Build ID.
        :param user_id: (integer)
            ID of owner.
        :param lang: (string)
            Language of owner.
        :param processing: (dictionary)
            A processing dictionary.
        :param pack: (dictionary)
            A pack dictionary.
        """
        self.uid = build_id
        self.agent_url = None
        self.agent_id = ''
        self._build_manager = build_manager
        self._lang = lang
        self._processing = processing
        self._pack = pack
        self._thread = None
        self._key = str(randint(1000, 9999999))
        self.expire = time() + build_manager.build_ttl
        self.result = {
            'status': 'none',
            'log': [(time(), 'wait', 1, self._translate(_('waiting...')))],
            'project_id': pack['project_id'], 'user_id': user_id}

    # -------------------------------------------------------------------------
    def start(self, request):
        """Start a build in a thread.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :return: (boolean)
        """
        if self._thread is not None:
            return True

        # Find agent
        self.agent_url, self.agent_id = self._build_manager.find_agent(
            request, self._processing['processor_id'])
        if self.agent_url is None:
            return False

        # Prepare synchronization
        if self.agent_url:
            if self._build_manager.call(
                    request, self.agent_url, 'synchronizing', self.uid)[0]:
                return False

        # Create thread
        self._thread = Thread(
            target=self._thread_start, kwargs={'request': request})
        self.result['log'] = [
            (time(), 'start', 1, self._translate(_('startup')))]
        try:
            self._thread.start()
        except RuntimeError as error:
            self._build_manager.call(
                request, self.agent_url, 'synchronizing', self.uid, False)
            self.stopped(error, 'a_warn')
            return False
        return True

    # -------------------------------------------------------------------------
    def progress(self, request):
        """Return the progress of build.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :return: (tuple)
            A tuple such as ``(<step>, <percent>, <message>, <start_time>,
            <agent_id)>)``.
        """
        if self.result['log'][-1][1][0:2] != 'a_':
            return self.result['log'][-1][1:] \
                + (self.result['log'][0][0], self.agent_id)

        error, prgrss = self._build_manager.call(
            request, self.agent_url, 'progress', self.uid)
        if error:
            self.stopped(error.decode('utf8'), 'a_error')
            return self.result['log'][-1][1:] \
                + (self.result['log'][0][0], self.agent_id)
        if prgrss[0] == 'none':
            self.stopped(_('agent build destroyed'))
            prgrss = self.result['log'][-1][1:]
        elif prgrss[0] in ('a_end', 'a_stop', 'a_fatal'):
            self.complete(request, self._key)
            prgrss = self.result['log'][-1][1:]
        return tuple(prgrss) + (self.result['log'][0][0], self.agent_id)

    # -------------------------------------------------------------------------
    def complete(self, request, key):
        """Start a *complete* action in a thread.

        :param request: (object)
            WebOb request object.
        :param key: (string)
            Authentication key.
        :return: (boolean)
            ``True`` if succeeds.
        """
        if self.result['log'][-1][1][0:2] != 'a_' or self._key != key or \
                (self._thread is not None and self._thread.is_alive()):
            return False
        self._log(_('getting log'), 'get', 91)

        # Update request
        user_id = int(self.result['user_id'])
        if 'user_id' not in request.session \
                or request.session['user_id'] != user_id:
            user = DBSession.query(User).filter_by(user_id=user_id).first()
            if user is None:
                self.stopped(_('unknown user'))
                DBSession.close()
                return False
            user.setup_environment(request)

        # Get result
        result = self._get_result(request)
        if result is None:
            DBSession.close()
            return False

        # Error or warning?
        warning = False
        for log in self.result['log']:
            if log[1] in ('error', 'a_error'):
                self.stopped(_('error occurred'))
                self._move2task(request, True)
                DBSession.close()
                return False
            elif log[1] in ('warn', 'a_warn'):
                warning = True

        # Transfer result
        if 'values' in result:
            self.result['values'] = result['values']
        if 'files' in result:
            self.result['files'] = result['files']

        # Download output directory in storage
        if self.result.get('files') and self._processing['output']:
            self._output2storage(request)
            if self.stopped():
                del self.result['files']
                self._move2task(request, True)
                DBSession.close()
                return False

        # End
        self.result['message'] = not warning and _('Successfully completed') \
            or _('Successfully completed but with warnings')
        self.result['status'] = 'end'
        self._log(self.result['message'], 'end', 100)
        self._move2task(request)
        DBSession.close()
        return True

    # -------------------------------------------------------------------------
    def stop(self, request=None):
        """Stop building."""
        if request is not None and self.result['log'][-1][1][0:2] == 'a_':
            error = self._build_manager.call(
                request, self.agent_url, 'stop', self.uid)[0]
            if error:
                self.stopped(error.decode('utf8'))
        elif not self.stopped():
            if self.result['log'][-1][1] == 'sync':
                self._build_manager.call(
                    request, self.agent_url, 'synchronizing', self.uid, False)
            self._log(_('stopped'), 'stop', 100)
            self.result['message'] = _('Stopped by user')
            self.result['status'] = 'stop'

    # -------------------------------------------------------------------------
    def stopped(self, error=None, level='fatal'):
        """Check if there is a fatal error and if the build is stopped.

        :param error: (string, optional)
            Error message.
        :param level: (string, default='fatal')
            Error level: ``warn``, ``error`` or ``fatal``.
        :return: (boolean)
            ``True`` if it is stopped.
        """
        if error:
            if level == 'fatal':
                self.result['status'] = level
                self.result['message'] = error
            self._log(error, level, 100)

        return self.result['status'] in ('stop', 'fatal', 'end')

    # -------------------------------------------------------------------------
    def _log(self, message, step=None, percent=None):
        """Append an entry to ``result['log']``.

        :param message: (string)
            Message to write to the log.
        :param step: (string, optional)
            If not ``None``, progress is updated.
        :param percent: (int, optional)
            Percent of progress for step ``<step>``.

        ``self.result['log']`` is a list of tuples such as ``(<timestamp>,
        <step>, <percent>, <message>)``.
        """
        if percent is None:
            percent = self.result['log'][-1][2] if step is None else 0

        if step is None:
            step = self.result['log'][-1][1]

        self.result['log'].append(
            (time(), step, percent, self._translate(message)))

    # -------------------------------------------------------------------------
    def _thread_start(self, request):
        """Action launched in a thread to start a build.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        """
        # Synchronize storages with buildspaces
        self.expire = time() + self._build_manager.build_ttl
        if self.agent_url:
            self._storage2buildspace(request)
            self._build_manager.start_waiting(request)
        if self.stopped():
            return

        # Start build
        self.expire = time() + self._build_manager.build_ttl
        end_url = request.route_url(
            'build_complete', build_id=self.uid, key=self._key)
        if self.agent_url:
            self._log(
                _('call agent "${a}"', {'a': self.agent_id}), 'a_call', 1)
        else:
            self._log(_('call local agent'), 'a_call', 1)
        error = self._build_manager.call(
            request, self.agent_url, 'start', self.uid, self._processing,
            self._pack, end_url)[0]
        self.stopped(error)

    # -------------------------------------------------------------------------
    def _storage2buildspace(self, request):
        """Synchronize storages on front with buildspaces on agent.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        """
        # Make list of files to synchronize
        file_list = list(self._processing['resources']) \
            + [k[0] for k in self._processing['templates']] \
            + list(self._pack['files']) \
            + list(self._pack['resources']) \
            + [k[0] for k in self._pack['templates']]
        total = len(file_list)

        # Browse names and synchronize
        self._log(_('synchronization'), 'sync', 1)
        for index, name in enumerate(file_list):
            self._log(
                _('agent "${a}" synchronizing of ${n}',
                  {'a': self.agent_id, 'n': name}),
                'sync', max(90 * index / total, 1))
            fullname = join(request.registry.settings['storage.root'], name)
            if not exists(fullname):
                continue
            if isfile(fullname):
                self._file2buildspace(request, name)
            else:
                self._dir2buildspace(request, name)
            if self.stopped():
                return

        self._log(_('synchronization completed'), 'syncend', 90)

    # -------------------------------------------------------------------------
    def _dir2buildspace(self, request, directory):
        """Synchronize a directory in storage on front with its copy in
        buildspace on agent.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param directory: (string)
            Relative path to storage directory of directory to synchronize.
        """
        # Get directory content
        fullpath = join(
            request.registry.settings['storage.root'], directory)
        file_list = []
        for path, dirs, files in walk(fullpath):
            for name in set(dirs) & set(EXCLUDED_FILES):
                dirs.remove(name)
            for name in files:
                file_list.append(relpath(join(path, name), fullpath))

        # In destination, remove deleted files
        error = self._build_manager.call(
            request, self.agent_url, 'buildspace_cleanup', directory,
            file_list)[0]
        if self.stopped(error):
            return

        # Synchronize files
        for name in file_list:
            self._file2buildspace(request, join(directory, name))
            if self.stopped():
                return

    # -------------------------------------------------------------------------
    def _file2buildspace(self, request, filename):
        """Synchronize a file in storage on front with its copy in buildspace
        on agent.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param filename: (string)
            Relative path to storage directory of file to synchronize.
        """
        # Get file signature
        error, sig = self._build_manager.call(
            request, self.agent_url, 'buildspace_send_signature', filename)
        if self.stopped(error):
            return
        stg_path = request.registry.settings['storage.root']

        # Transfer delta
        with open(join(stg_path, filename), 'rb') as hdl:
            delta_file = DeltaFile(sig.data, hdl)
            delta_buf = delta_file.read()
            delta_file.close()
        if len(delta_buf) < 512 or self.stopped():
            return
        error = self._build_manager.call(
            request, self.agent_url, 'buildspace_receive_delta', filename,
            xmlrpclib.Binary(delta_buf))[0]
        self.stopped(error)

    # -------------------------------------------------------------------------
    def _output2storage(self, request):
        """Copy output on agent in storage on front.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        """
        # Authorized?
        storage, root, user = self._storage4output(request)
        if storage is None:
            return

        # Local agent
        if not self.agent_url:
            output_dir = join(
                request.registry.settings['build.root'], camel_case(self.uid),
                'Output')
            if not exists(output_dir):
                self.stopped(_('Output directory has been destroyed.'))
                return
            files = output_dir
            copy_content(output_dir, root)
        # Remote agent
        else:
            self._log(_('getting files from "${a}"', {'a': self.agent_id}),
                      'sync', 92)
            error, files = self._build_manager.call(
                request, self.agent_url, 'output_list', self.uid)
            if self.stopped(error) or not len(files):
                return
            total = len(files)
            for index, filename in enumerate(files):
                self._log(_('getting ${f}', {'f': filename}),
                          'sync', 93 + 6 * index / total)
                self._file2storage(request, root, filename)
                if self.stopped():
                    return

        # Add in VCS
        handler = request.registry['handler'].get_handler(
            storage.storage_id, storage)
        if storage.vcs_engine != 'none':
            message = get_localizer(request).translate(
                _('Produced by processing'))
            handler.add(
                (user and user.vcs_user or None,
                 user and decrypt(
                     user.vcs_password,
                     request.registry.settings.get('encryption', '-')),
                 request.session['name']),
                self._processing['output'].partition('/')[2], message)
            error, message = handler.progress()
            if error == 'error':
                self.stopped(message)
        handler.cache.clear()

        # Add to pack
        if not self.stopped() and self._processing['add2pack']:
            self._result2pack(relpath(
                root, request.registry.settings['storage.root']), files)
        if not self.stopped():
            self._log(_('result received'), 'get', 99)

    # -------------------------------------------------------------------------
    def _file2storage(self, request, root, filename):
        """Synchronize a file in build directory on agent with one in storage
        on front.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param root: (string)
            Absolute root path for file to synchronize.
        :param filename: (string)
            Name of the file to synchronize.
        """
        fullname = normpath(join(root, filename))
        if not fullname.startswith(root):
            self.stopped(_('Access was denied to this resource.'))
            return
        if not exists(dirname(fullname)):
            makedirs(dirname(fullname))
        if not exists(fullname):
            with open(fullname, 'w') as hdl:
                hdl.write('')

        # Transfer delta
        sig_file = SigFile(open(fullname, 'rb'), get_block_size(fullname))
        sig_buf = sig_file.read()
        sig_file.close()
        error, delta = self._build_manager.call(
            request, self.agent_url, 'output_send_delta', self.uid, filename,
            xmlrpclib.Binary(sig_buf))
        if self.stopped(error):
            return

        # Patch
        patch_file = PatchedFile(open(fullname, 'rb'), StringIO(delta.data))
        temp_name = '%s~%d~' % (fullname, randint(1, 999999))
        with open(temp_name, 'wb') as hdl:
            hdl.write(patch_file.read())
        patch_file.close()
        if exists(temp_name):
            rename(temp_name, fullname)

    # -------------------------------------------------------------------------
    def _get_result(self, request):
        """Get the result dictionnary from the agent.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :return: (dictionary or ``None``)
        """
        error, result = self._build_manager.call(
            request, self.agent_url, 'result', self.uid)
        if self.stopped(error):
            self._move2task(request, True)
            return

        self.result['log'][-1:1] += result['log']

        if result['status'] == 'none':
            self.stopped(_('agent build destroyed'))
            self._move2task(request, True)
            return
        elif result['status'] != 'a_end':
            self.result['status'] = result['status'][2:]
            self.result['message'] = result['message']
            self._move2task(request, True)
            return

        return result

    # -------------------------------------------------------------------------
    def _storage4output(self, request):
        """Get the corresponding storage of an output if exists and if user
        is authorized.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :return: (tuple)
            A tuple such as ``(storage, root, user)`` where ``storage`` is
            a :class:`~.models.storages.Storage` object, ``root`` the
            absolute root path for files to transfer and ``user`` a
            :class:`~.models.storage.StorageUser` object.
        """
        # Root path
        storage_root = normpath(request.registry.settings['storage.root'])
        root = normpath(join(storage_root, self._processing['output']))
        if not root.startswith(storage_root):
            self.stopped(_('Access was denied to this resource.'))
            return None, None, None

        # Storage
        storage_id = self._processing['output'].partition('/')[0]
        try:
            storage = current_storage(request, storage_id, False)[0]
        except HTTPNotFound:
            self.stopped(_('This storage does not exist!'))
            return None, None, None
        except HTTPForbidden:
            self.stopped(_('You do not have access to this storage!'))
            return None, None, None
        if request.session['storage']['perm'] != 'writer':
            self.stopped(_('You cannot write into this storage!'))
            return None, None, None

        # Storage user
        user = DBSession.query(StorageUser).filter_by(
            storage_id=storage_id, user_id=request.session['user_id']).first()
        if storage.vcs_engine not in ('none', 'local') \
                and not (user and user.vcs_user):
            self.stopped(_('ID and password for storage are missing.'))
            return None, None, None

        return storage, root, user

    # -------------------------------------------------------------------------
    def _result2pack(self, base, result):
        """Add result into pack.

        :param base: (string)
            Base root for files to add.
        :param result: (string or list)
            Output directory where files are stored or list of files to add.
        """
        pack = DBSession.query(Pack).filter_by(
            project_id=self._pack['project_id'],
            pack_id=self._pack['pack_id']).first()
        if pack is None:
            return

        # File list
        packing = {}
        mode = self._processing['add2pack']
        if mode[:6] == 'result' or mode == 'smart':
            packing[mode == 'smart' and 'file' or mode[7:-1]] = \
                sorted(self.result.get('files'))
        if (mode[:6] == 'output' or mode == 'smart') and not self.agent_url:
            done = mode == 'smart' and set(self.result.get('files')) or ()
            mode = mode == 'smart' and 'resource' or mode[7:-1]
            packing[mode] = []
            for path, name, files in walk(result):
                for name in sorted(files):
                    if name not in EXCLUDED_FILES and '~' not in name \
                            and relpath(join(path, name), result) not in done:
                        packing[mode].append(relpath(join(path, name), result))
        if (mode[:6] == 'output' or mode == 'smart') and self.agent_url:
            done = mode == 'smart' and set(self.result.get('files')) or ()
            mode = mode == 'smart' and 'resource' or mode[7:-1]
            packing[mode] = []
            for name in sorted(result):
                if name not in EXCLUDED_FILES and '~' not in name \
                        and name not in done:
                    packing[mode].append(name)

        # Add to database
        for mode in packing:
            done = set([k.path for k in pack.files if k.file_type == mode])
            for name in packing[mode]:
                name = join(base, name)
                if name not in done:
                    pack.files.append(PackFile(mode, name))
        pack.updated = datetime.now()
        pack.update_sort()
        DBSession.commit()

        self._log(
            _('result added to pack (${t})', {
                't': self._translate(
                    ADD2PACK_TARGETS[self._processing['add2pack']])}),
            'get', 99)

    # -------------------------------------------------------------------------
    def _move2task(self, request, error=False):
        """According to ``error``, move managed pack to new task.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param error: (boolean, default=False)
            ``True`` if error.
        """
        target_task_id = (error and self._pack['task_ko']) \
            or (not error and self._pack['task_ok'].partition('#')[0])
        if not target_task_id and not error:
            return
        link_type = error and 'back' or self._pack['task_ok'].partition('#')[2]

        pack = DBSession.query(Pack).filter_by(
            project_id=self._pack['project_id'],
            pack_id=self._pack['pack_id']).first()
        if pack is not None:
            pack2task(request, pack, link_type, target_task_id)

    # -------------------------------------------------------------------------
    def _translate(self, text):
        """Return ``text`` translated.

        :param text: (string)
            Text to translate.
        """
        return localizer(self._lang or 'en').translate(text)
