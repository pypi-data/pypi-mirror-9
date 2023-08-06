# $Id: agent.py 7981fd623a54 2015/02/21 08:15:22 Patrick $
"""Agent build management.

An *agent* is a Web service.
"""

import logging
from os import listdir, makedirs
from os.path import exists, join, getatime, normpath, dirname, relpath
from os.path import getmtime
from lxml import etree
from threading import Thread
from time import time
from fnmatch import fnmatch
from shutil import rmtree, copy2
from glob import glob
import urllib

from pyramid.asset import abspath_from_asset_spec

from ..utils import _, localizer, copy_content, camel_case, settings_get_list
from ..xml import load


LOG = logging.getLogger(__name__)


# =============================================================================
class AgentBuildManager(object):
    """This class manages agent builds.

    One instance of :class:`AgentBuildManager` is created during application
    initialization. It is only used in agent mode. It is stored in application
    registry.

    ``self._processors`` is a tuple such as ``(processor_dictionary, root_list,
    available_list)``. ``processor_dictionary`` is a dictionary such as
    ``{processor_id: processor_path,...}``.

    ``self._fronts`` is a dictionary such as ``{front_id: password,...}``.

    ``self._builds`` is a dictionary of :class:`AgentBuild` objects.

    ``self._results`` is a dictionary of dictionaries such as ``{build_id:
    result_dict}``. ``result_dict`` is a dictionary with following keys:
    ``status``, ``log``, ``expire``. According to build events, it can also
    contains ``files``, ``values`` and ``error`` keys.

    ``self._results[build_id]['status']`` is one of the following strings:
    ``a_stop``, ``a_fatal`` or ``a_end``.

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
        self.settings = settings
        self.translation_dirs = [
            abspath_from_asset_spec(k)
            for k in settings_get_list(settings, 'translation_dirs')]
        self.build_ttl = int(settings.get('build.ttl', 1800))
        self.result_ttl = int(settings.get('build.result_ttl', 604800))
        self._concurrent = [
            int(settings.get('front.synchronize', 1)),
            int(settings.get('build.concurrent', 3))]
        self._buildspace_ttl = int(settings.get('buildspace.ttl', 2678400))
        self._syncs = {}
        self._builds = {}
        self._results = {}

        # Processor list
        self._processors = [
            {}, tuple(settings_get_list(settings, 'processor.roots')),
            tuple(settings_get_list(settings, 'processor.list'))]

        # Authorized front list
        self._fronts = {}
        for idx in range(100):
            if 'front.%d.uid' % idx in settings:
                self._fronts[settings['front.%d.uid' % idx]] = \
                    settings.get('front.%d.password' % idx, '')

        # Build directory cleaning
        if settings.get('build.reset') == 'true' \
           and exists(settings.get('build.root')):
            rmtree(settings.get('build.root'))

    # -------------------------------------------------------------------------
    def agent_id(self):
        """Get agent unique ID."""
        return self.settings['uid']

    # -------------------------------------------------------------------------
    def processor_list(self):
        """Refresh information and return a list of available processors and
        the number of possible concurrent builds.

        :return: (tuple)
            A tuple such as ``(processor_list, concurrent)``.
        """
        self._processors[0] = {}
        self.add_processors(join(dirname(__file__), '..', '..', 'Processors'))
        for path in self._processors[1]:
            self.add_processors(path)
        plist = []
        for pid in self._processors[0]:
            for pattern in self._processors[2]:
                if pid not in plist and fnmatch(pid, pattern):
                    plist.append(pid)
                    break
        return plist, self._concurrent[1]

    # -------------------------------------------------------------------------
    def add_processors(self, path):
        """Add all processors in path ``path``.

        :param path: (string)
             Where to look for processors.
        """
        path = abspath_from_asset_spec(path)
        if not exists(path):
            return

        for pid in listdir(path):
            if exists(join(path, pid, 'processor.xml')):
                self._processors[0][pid] = normpath(join(path, pid))

    # -------------------------------------------------------------------------
    def processor_path(self, processor_id):
        """Return processor path if exists.

        :param processor_id: (string)
            Processor ID.
        :return: (string)
        """
        return self._processors[0].get(processor_id)

    # -------------------------------------------------------------------------
    def processor_xml(self, processor_id):
        """Return processor XML if exists.

        :param processor_id: (string)
            Processor ID.
        :return: (string)
        """
        # Read main file
        if processor_id not in self._processors[0]:
            return ''
        parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
        relaxngs = {
            'publiforge':
            join(dirname(__file__), '..', '..', 'RelaxNG', 'publiforge.rng')}
        tree = load(
            join(self._processors[0][processor_id], 'processor.xml'),
            relaxngs=relaxngs, parser=parser)
        if isinstance(tree, basestring):
            return ''

        # Read variable files
        # pylint: disable = locally-disabled, maybe-no-member
        if tree.getroot().find('processor/variables/group-file') is not None:
            variables_elt = etree.Element('variables')
            for elt in tree.getroot().findall(
                    'processor/variables/group-file'):
                path = elt.text.strip()
                path = ':' in path and abspath_from_asset_spec(path) \
                    or join(self._processors[0][processor_id], path)
                var_tree = load(path, relaxngs=relaxngs, parser=parser)
                if isinstance(var_tree, basestring):
                    return ''
                for elt in var_tree.getroot().findall('variables/group'):
                    variables_elt.append(elt)
            tree.getroot().find('processor').replace(
                tree.getroot().find('processor/variables'), variables_elt)

        return etree.tostring(tree, encoding='utf8')

    # -------------------------------------------------------------------------
    def front_list(self):
        """Return a list of authorized fronts."""
        return self._fronts.keys()

    # -------------------------------------------------------------------------
    def authorized_front(self, front_id, password):
        """``True`` if ``front_id`` is authorized to use agent services."""
        return front_id in self._fronts and self._fronts[front_id] == password

    # -------------------------------------------------------------------------
    def activity(self):
        """Return the global activity i.e. the number of active or pending
        builds.

        :return: (integer)
             Number of builds or -1 if the maximum number is reached.
        """
        if len(self._syncs) >= self._concurrent[0] \
           or len(self._builds) + len(self._syncs) >= self._concurrent[1]:
            return -1
        return len(self._builds)

    # -------------------------------------------------------------------------
    def synchronizing(self, build_id, lock=True):
        """Data synchronization for the build ``build_id``.

        :param build_id: (string)
            Build ID.
        :param lock: (boolean, default=True)
            If ``True`` try to add build ``build_id`` in the list of
            synchronizations.
        :return: (boolean)
        """
        self._cleanup()
        if not lock:
            if build_id in self._syncs:
                del self._syncs[build_id]
            return True

        if len(self._syncs) >= self._concurrent[0] \
           or len(self._builds) + len(self._syncs) >= self._concurrent[1]:
            return False
        self._syncs[build_id] = time() + self.build_ttl
        return True

    # -------------------------------------------------------------------------
    def start_build(self, build_id, context, processing, pack, end_url=None):
        """Create a build, add it in ``self._builds`` dictionary and try to
        start it.

        :param build_id: (string)
            Build ID.
        :param context: (dictionary)
            See :class:`~.front.FrontBuildManager`
            :meth:`~.front.FrontBuildManager.call` method.
        :param processing: (dictionary)
            A processing dictionary.
        :param pack: (dictionary)
            A pack dictionary.
        :param end_url: (string, optional)
            URL to call to complete the build.
        :return: (:class:`~AgentBuild` or ``None``)
        """
        self._cleanup()
        self._cleanup_directories()
        if build_id in self._builds:
            return self._builds[build_id]

        self.synchronizing(build_id, False)
        if build_id in self._results:
            del self._results[build_id]
        if len(self._syncs) >= self._concurrent[0] \
           or len(self._builds) + len(self._syncs) >= self._concurrent[1]:
            return
        self._builds[build_id] = AgentBuild(
            self, build_id, context, processing, pack, end_url)
        self._builds[build_id].start()
        return self._builds[build_id]

    # -------------------------------------------------------------------------
    def progress(self, build_id):
        """Return the progress of build.

        :param build_id: (string)
            Build ID.
        :return: (tuple)
            A tuple such as ``(<step>, <percent>, <message>)``.

        The step ``<step>`` is one of the following:

        * ``a_start``: starting
        * ``a_env``: importing processor environment
        * ``a_build``: building
        * ``a_warn``: a warning occurred
        * ``a_error``: an error occurred
        * ``a_fatal``: a fatal error occurred
        * ``a_stop``: stopping
        * ``a_end``: successfully completed
        * ``none``: unknown or not in progress build
        """
        self._cleanup()
        if build_id in self._builds and self._builds[build_id].result['log']:
            return self._builds[build_id].result['log'][-1][1:]
        elif build_id in self._results:
            return self._results[build_id]['log'][-1][1:]
        return 'none', 0, ''

    # -------------------------------------------------------------------------
    def stop(self, build_id):
        """Stop a build.

        :param build_id: (string)
            Build ID.
        """
        self._cleanup()
        self.synchronizing(build_id, False)
        if build_id in self._builds:
            self._builds[build_id].stop()
        return ''

    # -------------------------------------------------------------------------
    def result(self, build_id):
        """Return the result of build.

        :param build_id: (string)
            Build ID.
        :return: (dictionary)
            ``self._result`` or ``{'status': 'none'}``.

        The status ``<status>`` is one of the following:

        * ``a_stop``: stopped
        * ``a_fatal``: a fatal error occurred
        * ``a_end``: successfuly completed
        * ``none``: unknown build
        """
        self._cleanup()
        return self._results[build_id] if build_id in self._results \
            else {'status': 'none', 'log': [], 'message': ''}

    # -------------------------------------------------------------------------
    def _cleanup(self):
        """Delete completed builds and expired results and kill long builds."""
        # Build -> result or stop
        now = time()
        for build_id in self._builds.keys():
            if self._builds[build_id].stopped():
                self._builds[build_id].result['expire'] = now + self.result_ttl
                self._results[build_id] = self._builds[build_id].result
                del self._builds[build_id]
            elif self._builds[build_id].expire < now:
                self._builds[build_id].stopped(_('timeout'))

        # Remove old results
        for build_id in self._results.keys():
            if now > self._results[build_id]['expire']:
                del self._results[build_id]

        # Remove too long synchronisations
        for build_id in self._syncs.keys():
            if self._syncs[build_id] < now:
                del self._syncs[build_id]

    # -------------------------------------------------------------------------
    def _cleanup_directories(self):
        """Remove old directories."""
        # Clean up buid path
        now = time()
        if exists(self.settings['build.root']):
            for name in listdir(self.settings['build.root']):
                path = join(self.settings['build.root'], name)
                if name not in self._builds and exists(path) \
                   and getatime(path) + self.result_ttl < now:
                    rmtree(path)

        # Clean up buidspace path
        if self.settings.get('buildspace.root') is not None \
                and exists(self.settings['buildspace.root']):
            for name in listdir(self.settings['buildspace.root']):
                path = join(self.settings['buildspace.root'], name)
                if exists(path) \
                        and getatime(path) + self._buildspace_ttl < now:
                    rmtree(path)


# =============================================================================
class AgentBuild(object):
    """This class manages one local build.

    ``self.result`` is a dictionary with the following keys: ``status``,
    ``message``, ``log``. Log entry is a list of tuples such as ``(<timestamp>,
    <step>, <percent>, <message>)``. Processor can add keys like: ``files``,
    ``values``.
    """
    # pylint: disable = locally-disabled, too-many-instance-attributes

    # -------------------------------------------------------------------------
    def __init__(self, build_manager, build_id, context, processing, pack,
                 end_url):
        """Constructor method.

        :param build_manager: (:class:`AgentBuildManager` instance)
            Application :class:`AgentBuildManager` object.
        :param build_id: (string)
            Build ID.
        :param context: (dictionary)
            See :class:`~publiforge.lib.build.front.FrontBuildManager`
            :meth:`~publiforge.lib.build.front.FrontBuildManager.call`
            method.
        :param processing: (dictionary)
            A processing dictionary.
        :param pack: (dictionary)
            A pack dictionary.
        :param end_url: (string, optional)
            URL to call to complete the build.
        """
        # pylint: disable = locally-disabled, too-many-arguments
        self._manager = build_manager
        self.settings = build_manager.settings
        self.build_id = build_id
        self.context = context
        self.path = join(
            build_manager.settings['build.root'], camel_case(build_id))
        self.data_path = \
            context['local'] and build_manager.settings.get('storage.root') \
            or build_manager.settings['buildspace.root']
        self.result = {
            'status': 'none',
            'log': [(time(), 'a_wait', 1, self._translate(_('waiting...')))],
            'message': ''}
        self.expire = time() + build_manager.build_ttl
        self.processing = processing
        self.pack = pack
        self._end_url = end_url
        self._thread = None
        if not exists(self.path):
            makedirs(self.path)

    # -------------------------------------------------------------------------
    def start(self):
        """Start the processing."""
        # Already started
        if self._thread is not None:
            self.stopped(_('Already in progress'), 'a_warn')
            return
        self.result['log'] = [(
            time(), 'a_start', 1, self._translate(_('agent build startup')))]

        # Create build directory
        path = join(self.path, 'Attic')
        if not exists(path):
            makedirs(path)
        path = join(self.path, 'Processor')
        if self.settings.get('build.develop') == 'true' and exists(path):
            rmtree(path)
        if not exists(path):
            makedirs(path)
            if not self._import_processor(self.processing['processor_id']):
                self.stopped(self.result['message'])
                return
            self.log(_('processor environment installed'), 'a_env', 1)
        path = join(self.path, 'Output')
        if exists(path):
            try:
                rmtree(path)
            except OSError as error:
                self.stopped(error)
                return
        makedirs(path)

        # Build directly...
        if self._end_url is None:
            self._thread_processor()
            return

        # ...or in a thread
        self._thread = Thread(target=self._thread_processor)
        self._thread.start()

    # -------------------------------------------------------------------------
    def stop(self):
        """Stop building."""
        if not self.stopped():
            self.result['status'] = 'a_stop'
            self.result['message'] = self._translate(_('Stop by user'))
            self.log(_('stopped'), 'a_stop', 90)

    # -------------------------------------------------------------------------
    def stopped(self, error=None, level='a_fatal'):
        """Check if there is a fatal error and if the build is stopped.

        :param error: (string, optional)
            Error message.
        :param level: (string, default='a_fatal')
            Error level: ``a_warn``, ``a_error`` or ``a_fatal``.
        :return: (boolean)
            ``True`` if it is stopped.
        """
        if error:
            if level == 'a_fatal':
                self.result['status'] = level
                self.result['message'] = self._translate(error)
            self.log(error, level, 90)

        return self.result['status'] in ('a_stop', 'a_fatal', 'a_end')

    # -------------------------------------------------------------------------
    def output2attic(self):
        """Copy the content of ``Output`` directory to ``Attic`` directory."""
        if not self.stopped():
            copy_content(join(self.path, 'Output'), join(self.path, 'Attic'))

    # -------------------------------------------------------------------------
    def get_in_attic(self, target, dependencies=None, relations=None):
        """Try to retrieve the last version of a file in the attic and copy it
        in the ``Output`` directory.

        :param target: (string)
            Path to target file.
        :param dependencies: (list, optional)
            List of files to compare with to known if it is necessary to
            process.
        :param relations: (list, optional)
            List of closely related files to retrieve with the target file.
        :return: (boolean)
            ``True`` if the operation succeeded.
        """
        if self.processing['variables'].get('force'):
            return False

        # Get file in attic
        archive = join(
            self.path, 'Attic', relpath(target, join(self.path, 'Output')))
        if not exists(archive):
            return False

        # Get the more recent date in dependencies
        last_one = 0
        if dependencies is not None:
            for pattern in dependencies:
                if '*' not in pattern and '?' not in pattern \
                   and not exists(pattern):
                    return False
                for filename in glob(pattern):
                    file_time = getmtime(filename)
                    if last_one < file_time:
                        last_one = file_time

        # Nothing to do
        if dependencies is not None \
           and (not last_one or getmtime(archive) < last_one):
            return False

        # Retrieve related files
        relations = relations is not None and relations or []
        for pattern in relations:
            pattern = join(
                self.path, 'Attic',
                relpath(pattern, join(self.path, 'Output')))
            if '*' not in pattern and '?' not in pattern \
               and not exists(pattern):
                return False
            for filename in glob(pattern):
                relation = join(
                    self.path, 'Output',
                    relpath(filename, join(self.path, 'Attic')))
                copy2(filename, relation)

        # Copy archive in output directory
        if not exists(dirname(target)):
            makedirs(dirname(target))
        copy2(archive, target)

        return True

    # -------------------------------------------------------------------------
    def log(self, message, step=None, percent=None):
        """Append an entry to ``result['log']``.

        :param message: (string)
            Message to write in log.
        :param step: (string, optional)
            If not ``None``, progress is updated.
        :param percent: (int, optional)
            Percent of progress for step ``<step>``.
        """
        if percent is None:
            percent = self.result['log'][-1][2] if step is None else 0
        if step is None:
            step = self.result['log'][-1][1]

        self.result['log'].append(
            (time(), step, percent, self._translate(message)))

        if self.context['local'] and 'request' not in self.context:
            {
                'a_warn': LOG.warning, 'a_error': LOG.error,
                'a_fatal': LOG.critical
            }.get(step, LOG.info)(self.result['log'][-1][3])

    # -------------------------------------------------------------------------
    def _thread_processor(self):
        """Action in a thread to launch processor."""
        # Find the processor
        tree = etree.parse(join(self.path, 'Processor', 'processor.xml'))
        module_name = tree.findtext('processor/module').strip()
        try:
            module = __import__(module_name, fromlist=['Processor'])
        except ImportError as err:
            self.stopped('%s: %s' % (module_name, err))

        # Launch processor
        if not self.stopped():
            self.log(_('start processor'), 'a_build', 1)
            self.expire = time() + self._manager.build_ttl
            module.Processor(self).start()
            if not self.stopped():
                self.log(_('agent build completed'), 'a_end', 90)
                self.result['status'] = 'a_end'

        # Announce the end to the front
        if not self.context['local']:
            self._manager.synchronizing(self.build_id)
            try:
                response = urllib.urlopen(self._end_url)
            except IOError as err:
                self._manager.synchronizing(self.build_id, False)
                return
            response.close()
            self._manager.synchronizing(self.build_id, False)
        elif 'request' in self.context:
            request = self.context['request']
            request.registry['fbuild'].complete(
                request, self.build_id, self._end_url.split('/')[-1])

    # -------------------------------------------------------------------------
    def _import_processor(self, processor_id):
        """Import processor, eventually with inheritance, in build directory.

        :param processor_id: (string)
            ID of processor to import.
        :return: (boolean)
            ``True`` if it succeeds.
        """
        # Find processor
        src_path = self._manager.processor_path(processor_id)
        if not src_path:
            self.stopped(_('unknown processor "${p}"', {'p': processor_id}))
            return False

        # Read processor.xml file to check if other processors are needed
        ancestors = etree.parse(join(src_path, 'processor.xml'))\
            .findall('processor/ancestors/ancestor')
        for ancestor in ancestors:
            if not self._import_processor(ancestor.text.strip()):
                return False

        # Copy processor
        copy_content(
            src_path, join(self.path, 'Processor'),
            exclude=('Templates', 'Variables'), force=True)
        if exists(join(src_path, 'Templates')):
            copy_content(
                join(src_path, 'Templates'),
                join(self.path, 'Processor', 'Templates', processor_id),
                force=True)
        return True

    # -------------------------------------------------------------------------
    def _translate(self, text):
        """Return ``text`` translated.

        :param text: (string)
            Text to translate.
        """
        return localizer(
            self.context['lang'],
            self._manager.translation_dirs +
            [join(dirname(__file__), '..', '..', 'Locale')]).translate(text)
