# $Id: __init__.py 27712e4d14f8 2014/11/10 10:44:22 Patrick $
"""This processor makes Publiset XML file from a pack structure."""

from os import makedirs, walk, listdir, remove, rmdir
from os.path import join, exists, dirname, isdir, relpath, samefile, basename
from ConfigParser import ConfigParser
from lxml import etree
from shutil import copy, rmtree
import fnmatch
import re

from ...utils import _, config_get, config_get_list, normalize_spaces
from ...utils import make_id, camel_case
from ...xml import PUBLIFORGE_RNG_VERSION, load
from .. import load_relaxngs
from ..leprisme.transform import Transform
from ..leprisme.publiset import Publiset


# =============================================================================
class Processor(object):
    """Main class for Publiseter processor."""

    # -------------------------------------------------------------------------
    def __init__(self, build):
        """Constructor method.

        :param build: (:class:`~.lib.build.agent.AgentBuild`)
            Main Build object.
        """
        # Attributes
        self.build = build
        self.output = join(self.build.path, 'Output')
        self.percents = [1, 90]
        self.scripts = {}

        # Configuration
        name = join(build.path, 'Processor', 'publiseter.ini')
        if not exists(name):
            build.stopped(_('File "publiseter.ini" is missing.'))
            return
        self._config = ConfigParser({'here': dirname(name), 'fid': '{fid}'})
        self._config.read(name)

        # Relax NG
        self.relaxngs = load_relaxngs(self.build, self._config)

        # Transformation
        self._transform = Transform(self, [''])

    # -------------------------------------------------------------------------
    def start(self):
        """Start the processor."""
        if self.build.stopped():
            return

        # Publiset ID
        fid = make_id(
            self.build.processing['variables'].get('id'), 'token')
        if not fid:
            fid = make_id(self.build.pack['label'], 'token')

        # Update output
        subdir = self.build.processing['variables'].get('subdir')
        if subdir:
            self.output = join(
                self.build.path, 'Output',
                subdir.replace('%(fid)s', camel_case(fid)))
        else:
            self.output = join(self.build.path, 'Output')

        # Create directories
        for name in config_get_list(
                self._config, 'Initialization', 'directories'):
            if not exists(join(self.output, name)):
                makedirs(join(self.output, name))

        # Transform pack into Publiset
        self._transform.start('%s.xml' % fid, fid, self._create_pack())

        # Transform Publiset
        if self.build.processing['variables'].get('assembly'):
            self._assembly(fid)

        # Clean up
        self.finalize(True)

    # -------------------------------------------------------------------------
    def config(self, section, option, default=None):
        """Retrieve a value from a configuration object.

        :param section: (string)
            Section name.
        :param option: (string)
            Option name.
        :param default: (string, optional)
            Default value
        :return: (string)
            Read value or default value.
        """
        return config_get(self._config, section, option, default)

    # -------------------------------------------------------------------------
    def config_list(self, section, option, default=None):
        """Retrieve a list of values from a configuration object.

        :param section: (string)
            Section name.
        :param option: (string)
            Option name.
        :param default: (list, optional)
            Default values.
        :return: (list)
        """
        return config_get_list(self._config, section, option, default)

    # -------------------------------------------------------------------------
    def finalize(self, force=False):
        """Finalization."""
        if not force or self.build.processing['variables'].get('keeptmp'):
            return
        regex = self.config(
            'Finalization', 'remove_regex', r'(~|\.tmp)(\.\w{1,4})?$')
        for path, dirs, files \
                in walk(join(self.build.path, 'Output'), topdown=False):
            for name in dirs:
                if (regex and re.search(regex, name)) \
                        or not listdir(join(path, name)):
                    rmtree(join(path, name))
            for name in files:
                if regex and re.search(regex, name):
                    remove(join(path, name))

        if exists(self.output) \
                and not samefile(self.output, join(self.build.path, 'Output'))\
                and not listdir(self.output):
            rmdir(self.output)

    # -------------------------------------------------------------------------
    def _create_pack(self):
        """Create the XML pack.

        :return: (:class:`lxml.etree.Element` instance)
        """
        root = etree.Element('publiforge', version=PUBLIFORGE_RNG_VERSION)
        pack_elt = etree.SubElement(root, 'pack')
        etree.SubElement(pack_elt, 'label').text = \
            normalize_spaces(self.build.pack['label'])
        files_elt = etree.SubElement(pack_elt, 'files')

        prefix = None
        if not self.build.processing['variables'].get('assembly'):
            prefix = '%s-' % camel_case(self.build.context['front_id'])
        excluded = self.build.processing['variables'].get('file_exclude')
        excluded = excluded and re.compile(excluded) or None
        included = self.build.processing['variables'].get('file_include')
        included = included and re.compile(included) or None

        for name in self.build.pack['files']:
            fullname = join(self.build.data_path, name)
            if isdir(fullname) and self.build.pack['recursive']:
                for path, name, files in walk(fullname):
                    for name in sorted(fnmatch.filter(files, '*.xml')):
                        if not self._keep_it(excluded, included, name):
                            continue
                        name = relpath(join(path, name), self.build.data_path)
                        name = prefix and name.partition(prefix)[2] or name
                        name = isinstance(name, unicode) and name\
                            or name.decode('utf8')
                        etree.SubElement(files_elt, 'file').text = name
            elif isdir(fullname):
                for name in sorted(fnmatch.filter(listdir(fullname), '*.xml')):
                    if not self._keep_it(excluded, included, name):
                        continue
                    name = relpath(join(fullname, name), self.build.data_path)
                    name = prefix and name.partition(prefix)[2] or name
                    name = isinstance(name, unicode) and name\
                        or name.decode('utf8')
                    etree.SubElement(files_elt, 'file').text = \
                        name.decode('utf8')
            elif self._keep_it(excluded, included, basename(name)):
                etree.SubElement(files_elt, 'file').text = \
                    prefix and name.partition(prefix)[2] or name

        return root

    # -------------------------------------------------------------------------
    def _assembly(self, fid):
        """Realize the assembly.

        :param fid: (string)
            Publiset file ID.
        """
        # Load the Publiset
        # pylint: disable = locally-disabled, E1103
        root = load(join(
            self.output, self.config('Output', 'format', '').format(fid=fid)))
        if isinstance(root, basestring):
            self.build.stopped(root)
            return

        # Process
        data_path = join(
            self.build.data_path, self.build.processing['variables']
            .get('div1_path', '').replace('..', '-'))
        publiset = Publiset(self, data_path)
        set_root = root.find('composition')
        if set_root is None:
            self.build.stopped(_('Empty composition!'))
            return
        self.build.log(_('${f}: document composition', {'f': fid}))
        self._transform.start(
            '%s.xml' % fid, fid, publiset.compose('%s.xml' % fid, set_root))

    # -------------------------------------------------------------------------
    @classmethod
    def _keep_it(cls, excluded, included, filename):
        """Check if the file ``filename`` is kept according to ``excluded`` and
        ``included``.

        :param excluded: (:class:`re` object)
            Regular expression to define file to exclude.
        :param included: (:class:`re` object)
            Regular expression to define file to include.
        :param filename: (string)
            Name of file to check.
         :return: (boolean)
        """
        if excluded and excluded.search(filename):
            return False
        if included and not included.search(filename):
            return False
        return True
