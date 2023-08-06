# $Id: __init__.py 016a18098513 2015/02/10 16:03:46 Patrick $
"""LePrisme processor."""

from os import walk, listdir, makedirs, remove, rmdir
from os.path import join, exists, splitext, dirname, basename, isdir, relpath
from os.path import normpath, getmtime, samefile, commonprefix
from shutil import copy, rmtree
from ConfigParser import ConfigParser
from imp import load_source
from lxml import etree
from zipfile import is_zipfile
import re

from ...utils import _, copy_content, unzip, config_get, camel_case, make_id
from ...utils import config_get_list
from ...xml import load
from .. import load_relaxngs
from .publiset import Publiset
from .transform import Transform


REMOVE_PATTERN = r'(~|\.tmp)(\.\w{1,4})?$'


# =============================================================================
class Processor(object):
    """Main class for LePrisme processor."""

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

        # Configuration
        name = join(build.path, 'Processor', 'leprisme.ini')
        if not exists(name):
            build.stopped(_('File "leprisme.ini" is missing.'))
            return
        self._config = ConfigParser({
            'here': dirname(name), 'fid': '{fid}', 'ocffile': '{ocffile}'})
        self._config.optionxform = str
        self._config.read(name)

        # Transformation steps
        steps = self._read_steps()
        if not steps:
            build.stopped(_('Transformation steps are missing.'))
            return

        # Relax NG, scripts and transformation
        self.relaxngs = load_relaxngs(self.build, self._config)
        self._scripts = self._load_scripts()
        self._transform = Transform(self, steps)

    # -------------------------------------------------------------------------
    def start(self):
        """Start the processor."""
        if self.build.stopped():
            return

        # Initialization
        subdir = self.build.processing['variables'].get('subdir')
        if not subdir:
            self._initialize()
        if self.build.stopped():
            return

        # Process each file
        files = self._file_list()
        if not len(files):
            self.build.stopped(_('nothing to do!'), 'a_error')
            return
        for count, name in enumerate(files):
            self._process(
                name, 90 * count / len(files), 90 * (count + 1) / len(files))
            if self.build.stopped():
                break

        # Finalization
        if not subdir:
            self.output = join(self.build.path, 'Output')
            self.finalize()

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
    def finalize(self):
        """Finalization."""

        # Remove temporary files
        if not self.build.processing['variables'].get('keeptmp'):
            self._remove_temporary_files(self.output)

        # Run finalization script
        if 'finalization' in self._scripts:
            self._scripts['finalization'](self)

    # -------------------------------------------------------------------------
    def _read_steps(self):
        """Detect in configuration file the names of the transformation steps.

        :return: (tuple)
            A tuple of suffix for ``[Transformation]`` section.
        """
        steps = []
        for section in self._config.sections():
            if section.startswith('Transformation'):
                if self._config.has_option(section, 'inactive'):
                    inactive = self._config.get(section, 'inactive')
                    variable = self.build.processing['variables'].get(
                        inactive.replace('!', ''))
                    if (inactive[0] == '!' and not variable) \
                       or (inactive[0] != '!' and variable):
                        continue
                steps.append(section[14:])
        return tuple(steps)

    # -------------------------------------------------------------------------
    def _load_scripts(self):
        """Load initialization and finalization script files.

        :return: (dictionary)
            A dictionary of script main functions.
         """
        scripts = {}
        for section in ('Initialization', 'Finalization'):
            # Find file
            filename = self.config(section, 'script')
            if not filename:
                continue
            if not exists(filename):
                self.build.stopped(_('Unknown file "${n}".', {'n': filename}))
                continue

            # Load module
            module = load_source(splitext(basename(filename))[0], filename)
            scripts[section.lower()] = module.main

        return scripts

    # -------------------------------------------------------------------------
    def _update_output(self, filename, fid):
        """Compute output directory for file ``filename``.

        :param filename: (string)
            Relative path to the original file to transform.
        :param fid: (string)
            File ID.
        :return: (string)
            Output path.
        """
        subdir = self.build.processing['variables'].get('subdir')
        if subdir:
            prefix = commonprefix(
                tuple(self.build.pack['files']) + (filename,))
            if not isdir(prefix):
                prefix = dirname(prefix)
            filename = relpath(filename, prefix)
            self.output = join(
                self.build.path, 'Output',
                subdir.replace('%(fid)s', camel_case(fid))
                .replace('%(path)s', dirname(filename)))
        else:
            self.output = join(self.build.path, 'Output')

    # -------------------------------------------------------------------------
    def _file_list(self):
        """List files in pack according to settings.

        :return: (list)
            File list.
        """
        regex = self._config.has_option('Input', 'file_regex') \
            and re.compile(self.config('Input', 'file_regex'))
        input_is_dir = self._config.has_option('Input', 'is_dir') \
            and self.config('Input', 'is_dir') == 'true'
        files = []

        for base in self.build.pack['files']:
            fullname = normpath(join(self.build.data_path, base))
            if not exists(fullname):
                self.build.stopped(_('Unknown file "${n}".', {'n': base}))
                continue

            if (not regex or regex.search(base)) \
                    and isdir(fullname) == input_is_dir:
                files.append(base)
            if not isdir(fullname):
                if base not in files:
                    self.build.stopped(
                        _('"${n}" ignored', {'n': base}), 'a_warn')
                continue

            if self.build.pack.get('recursive'):
                for path, dirs, filenames in walk(fullname):
                    names = input_is_dir and dirs or filenames
                    for name in names:
                        if not regex or regex.search(name):
                            name = relpath(
                                join(path, name), self.build.data_path)
                            name = isinstance(name, str) \
                                and unicode(name.decode('utf8')) or name
                            files.append(name)
            else:
                for name in listdir(fullname):
                    if isdir(join(fullname, name)) == input_is_dir \
                            and (not regex or regex.search(name)):
                        name = relpath(
                            join(fullname, name), self.build.data_path)
                        name = isinstance(name, str) \
                            and unicode(name.decode('utf8')) or name
                        files.append(name)

        return files

    # -------------------------------------------------------------------------
    def _initialize(self, fid=None):
        """Initialization.

        :param fid: (string, optional)
            File ID.

        ``self.build.processing['templates']`` and
        ``self.build.pack['templates']`` are lists of tuples such as
        ``(<input_file>, <output_path>)``.
        """
        # Check
        if not self.output.startswith(self.build.path):
            self.build.stopped(_('file outside build directory'))
            return

        # Clean up
        # pylint: disable = locally-disabled, no-member
        if not exists(self.output):
            makedirs(self.output)
        fmt = self.config('Output', 'format')
        if fid and fmt and exists(join(self.output, fmt.format(fid=fid))):
            remove(join(self.output, fmt.format(fid=fid)))
        self._remove_temporary_files(
            self.output,
            fid and self._config.has_option('Input', 'unzip') and '%s~' % fid)

        # Create directories
        for name in self.config_list('Initialization', 'directories'):
            if not exists(join(self.output, name)):
                makedirs(join(self.output, name))

        # Copy templates
        if not self._copy_templates():
            return

        # Run initialization script
        if 'initialization' in self._scripts:
            self._scripts['initialization'](self)

    # -------------------------------------------------------------------------
    def _process(self, filename, percent_in, percent_out):
        """Process one XML file.

        :param filename: (string)
            Relative path of the file to process.
        :param percent_in: (integer)
            Percent of progress by entering the processing.
        :param percent_out: (integer)
            Percent of progress by leaving the processing.
        """
        if self.build.stopped():
            return

        # Load path
        fid = make_id(
            splitext(basename(filename))[0],
            self.config('Output', 'make_id', 'token'))
        fullname = normpath(join(self.build.data_path, filename))
        self.percents = [max(percent_in, 1), percent_out]
        self.build.log(
            u'%s ............' % fid, step='a_build', percent=self.percents[0])
        self._update_output(filename, fid)

        # Load folder
        if isdir(fullname):
            self._initialize(fid)
            self._transform.start(filename, fid, filename)
            return

        # Unzip file
        if self.config('Input', 'unzip') and is_zipfile(fullname):
            self.percents[0] = min(self.percents[0] + 1, self.percents[1])
            self.build.log(
                _('${f}: uncompressing', {'f': fid}), percent=self.percents[0])
            unzip(fullname, join(self.output, '%s~' % fid))
            fullname = join(
                self.output, '%s~' % fid, self.config('Input', 'unzip'))

        # Load file content
        self.percents[0] = min(self.percents[0] + 1, self.percents[1])
        self.build.log(
            _('${f}: loading file content', {'f': fid}),
            percent=self.percents[0])
        data = self._file_content(fullname, filename)
        if data is None:
            if self._config.has_option('Input', 'unzip') \
                    and isdir(join(self.output, '%s~' % fid)):
                rmtree(join(self.output, '%s~' % fid))
            return

        # Non Publiset file
        # pylint: disable = locally-disabled, E1103
        if isinstance(data, basestring) or data.getroot().tag != 'publiset':
            self._initialize(fid)
            self._transform.start(filename, fid, data)
            return

        # Publiset selection
        publiset = Publiset(self, dirname(fullname))
        for set_root in data.findall('selection'):
            for file_elt in set_root.xpath('.//file'):
                name = relpath(publiset.fullname(file_elt),
                               self.build.data_path)
                if name != filename:
                    self._process(name, percent_in, percent_out)
                if self.build.stopped():
                    return
            fid = set_root.get('id')
            self.build.log(
                u'%s ............' % fid, step='a_build',
                percent=self.percents[0])
            self._update_output(filename, fid)
            self._initialize(fid)
            self._transform.start(filename, fid, publiset.create(set_root))

        # Publiset composition
        self.percents[0] = min(self.percents[0] + 1, self.percents[1])
        for set_root in data.findall('composition'):
            fid = set_root.get('id')
            self.build.log(_('${f}: document composition', {'f': fid}))
            self._update_output(filename, fid)
            self._initialize(fid)
            self._transform.start(
                filename, fid, publiset.compose(filename, set_root))
            if self.build.stopped():
                return

    # -------------------------------------------------------------------------
    def _file_content(self, fullname, filename):
        """Load file content.

        :param fullname: (string)
            Full path to file to load.
        :param filename: (string)
            Relative path for messages.
        :return: (string or :class:`lxml.etree.ElementTree` instance or
            ``None``)
        """
        # Content regex
        regex = self.config('Input', 'content_regex')

        # XML file
        if splitext(fullname)[1].lower() == '.xml':
            relaxngs = self.relaxngs \
                if self.config('Input', 'validate') == 'true' else None
            data = load(fullname, relaxngs)
            if isinstance(data, basestring):
                if regex and exists(fullname):
                    with open(fullname, 'r') as hdl:
                        data = re.search(regex, hdl.read()) and data
                self.build.stopped(data, 'a_error')
                return
            if not regex or re.search(regex, etree.tostring(data)):
                return data
            self.build.stopped(_('"${n}" ignored', {'n': filename}), 'a_warn')
        # Other
        elif exists(fullname):
            with open(fullname, 'r') as hdl:
                data = hdl.read()
            if not regex or re.search(regex, data):
                return data
            self.build.stopped(_('"${n}" ignored', {'n': filename}), 'a_warn')
        else:
            self.build.stopped(_('Unknown file "${n}".', {'n': filename}))

    # -------------------------------------------------------------------------
    def _copy_templates(self):
        """Copy processor, processing and pack templates into ``Output``
        directory.

        :return: (boolean)
        """
        # Copy template files from INI files
        for name in self.config_list('Initialization', 'templates'):
            template = join(self.build.path, 'Processor', 'Templates', name)
            if not exists(template):
                self.build.stopped(
                    _('Template "${t}" does not exist', {'t': name}))
                return False
            path = self.config('template:%s' % name, 'path', '')
            copy_content(
                template, join(self.output, path), self._excluded_list(name))

        # Copy template files from processing and pack templates
        for name, path in self.build.processing['templates'] \
                + self.build.pack['templates']:
            template = join(self.build.data_path, name)
            if not exists(template):
                self.build.stopped(
                    _('Template "${t}" does not exist', {'t': name}))
                return False
            do_unzip = path[0:6] == 'unzip:'
            path = do_unzip and join(self.output, path[6:]) \
                or join(self.output, path)
            if isdir(template):
                copy_content(template, path)
            elif do_unzip and is_zipfile(template):
                unzip(template, path)
            else:
                if not exists(dirname(path)):
                    makedirs(dirname(path))
                copy(template, path)

        return True

    # -------------------------------------------------------------------------
    def _excluded_list(self, template):
        """Return exluded file list.

        :param template: (string)
            Template name.
        :return: (list)
        """
        exclude = []
        section = 'template:%s' % template
        if not self._config.has_section(section):
            return exclude

        for option in self._config.options(section):
            if option == 'exclude':
                exclude += self.config_list(section, option)
            elif option.startswith('exclude['):
                var_name = option[8:-1]
                if var_name[0] != '!' \
                        and self.build.processing['variables'].get(var_name):
                    exclude += self.config_list(section, option)
                elif var_name[0] == '!' and not \
                        self.build.processing['variables'].get(var_name[1:]):
                    exclude += self.config_list(section, option)

        return exclude

    # -------------------------------------------------------------------------
    def _remove_temporary_files(self, output, keep_dir=None):
        """Remove temporary files.

        :param output: (string)
            Full path to output directory.
        :param keep_dir: (string, optional)
            Name of directory to keep.
        """
        regex = re.compile(self.config(
            'Finalization', 'remove_regex', REMOVE_PATTERN))
        for path, dirs, files in walk(output, topdown=False):
            for name in dirs:
                if name != keep_dir and \
                   (regex.search(name) or not listdir(join(path, name))):
                    rmtree(join(path, name))
            for name in files:
                if regex.search(name):
                    remove(join(path, name))

        if exists(output) \
                and not samefile(output, join(self.build.path, 'Output')) \
                and not listdir(output):
            rmdir(output)
