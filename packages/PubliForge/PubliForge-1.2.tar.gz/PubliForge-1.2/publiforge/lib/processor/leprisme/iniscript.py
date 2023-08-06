# $Id: iniscript.py 7981fd623a54 2015/02/21 08:15:22 Patrick $
"""INI scripts management."""

from os import walk, rename, environ
from os.path import join, exists, dirname, basename, splitext, isfile, isabs
from os.path import normpath
from shlex import split
from ConfigParser import ConfigParser
import codecs
import sys

from ...utils import _, EXCLUDED_FILES, config_get, config_get_list, execute


MEDIA_EXT = {
    'image': ('svg', 'png', 'tif', 'tiff', 'jpg', 'jpeg', 'pdf', 'eps', 'gif'),
    'audio': ('wav', 'ogg', 'aac', 'ac3', 'mp3'),
    'video': ('dv', 'mpg', 'ogv', 'mp4', 'mov', 'avi', 'webm', 'flv')}


# =============================================================================
class IniScript(object):
    """Class for INI script managment."""

    # -------------------------------------------------------------------------
    def __init__(self, processor):
        """Constructor method.

        :param processor: (:class:`~.lib.processor.leprisme.Processor` object)
            Processor object on which it depends.
        """
        self._processor = processor

    # -------------------------------------------------------------------------
    def convert_media(self, filename, ini_file, done_tag, percent):
        """Convert a media (image, audio or video).

        :param filename: (string)
            Relative path to the original file to transform.
        :param ini_file: (string)
            Path to INI file.
        :param done_tag: (string)
            Tag to mark the once the conversion is done.
        :param percent: (integer)
            Percentage of progress.
        :return: (boolean)
        """
        # Read INI file
        config = ConfigParser({
            'here': dirname(ini_file),
            'bin': self._bin(),
            'output': self._processor.output,
            'processor': join(self._processor.build.path, 'Processor'),
            'donetag': done_tag,
            'lang': self._processor.build.context['lang'],
            'filepath':
            join(self._processor.build.data_path, dirname(filename)),
            'stgpath': self._processor.build.data_path,
            'id': '{id}', 'ext': '{ext}',
            'source': '{source}', 'sourcepath': '{sourcepath}',
            'target': '{target}', 'targetpath': '{targetpath}'})
        config.readfp(codecs.open(ini_file, 'r', 'utf8'))

        # Compute full path to source
        media_id = config_get(config, 'Source', 'id')
        media_type = config_get(config, 'Source', 'type')
        target = config_get(config, 'Target', 'file')
        source = self._find_media(
            media_type, media_id, config_get_list(config, 'Source', 'search'),
            target)
        if not source or not exists(source):
            self._processor.build.stopped(
                _('${f}: (${t}) no source for "${i}"',
                  {'f': basename(ini_file)[:-5], 't': media_type,
                   'i': media_id}), 'a_error')
            self._rename_ini(ini_file, done_tag)
            return False

        # Read full path to target
        if not target:
            self._processor.build.stopped(
                _('${f}: (${t}) no target for "${i}"',
                  {'f': basename(ini_file)[:-5], 't': media_type,
                   'i': media_id}), 'a_error')
            self._rename_ini(ini_file, done_tag)
            return False

        # Try to retrieve
        if self._get_in_attic(config, media_id, source, target):
            self._processor.build.log(
                _('${f}: (${t}) retrieving of "${i}"',
                  {'f': basename(ini_file)[:-5], 't': media_type,
                   'i': basename(target)}), step='a_build', percent=percent)
            self._rename_ini(ini_file, done_tag)
            return True

        # Transform data
        self._processor.build.log(
            _('${f}: (${t}) creation of "${i}"',
              {'f': basename(ini_file)[:-5], 't': media_type,
               'i': basename(target)}), step='a_build', percent=percent)
        section = 'Transformation:%s' % splitext(source)[1][1:]
        if not config.has_section(section):
            section = 'Transformation'
        for step in range(100):
            cmd = config_get(config, section, 'step.%d' % step)
            if cmd:
                cmd = cmd.format(
                    id=media_id, source=source, sourcepath=dirname(source),
                    target=target, targetpath=dirname(target))
                error = execute(split(cmd.encode('utf8')), dirname(ini_file))
                if error[1]:
                    self._processor.build.stopped(error[0], 'a_error')
                    self._processor.build.stopped(error[1])
                    self._rename_ini(ini_file, done_tag)
                    return False
        if not exists(target):
            self._processor.build.stopped(
                _('${f}: (${t}) unable to make "${i}"',
                  {'f': basename(ini_file)[:-5], 't': media_type,
                   'i': media_id}), 'a_error')
            self._rename_ini(ini_file, done_tag)
            return False
        self._rename_ini(ini_file, done_tag)
        return True

    # -------------------------------------------------------------------------
    def post_execution(self, ini_file, target_file, done_tag):
        """Process post INI script.

        :param ini_file: (string)
            Path to INI file.
        :param target_file: (string)
            Path to target file.
        :param done_tag: (string)
            Tag to mark the once the conversion is done.
        """
        config = ConfigParser({
            'here': dirname(ini_file),
            'bin': self._bin(),
            'output': self._processor.output,
            'processor': join(self._processor.build.path, 'Processor'),
            'donetag': done_tag,
            'lang': self._processor.build.context['lang'],
            'target': target_file})
        config.readfp(codecs.open(ini_file, 'r', 'utf8'))

        for step in range(100):
            cmd = config_get(config, 'Transformation', 'step.%d' % step)
            if cmd:
                log = execute(
                    split(cmd.encode('utf8')), self._processor.output)
                if log[1]:
                    self._processor.build.stopped(log[0], 'a_error')
                    self._processor.build.stopped(log[1])
                    self._rename_ini(ini_file, done_tag)
                    return
                if log[0]:
                    self._processor.build.log(log[0])

        self._rename_ini(ini_file, done_tag)

    # -------------------------------------------------------------------------
    def _find_media(self, media_type, media_id, patterns, target):
        """Look for a media.

        :param media_type: (string)
            Type of media (image, audio or video).
        :param media_id: (string)
            Media ID.
        :param patterns: (list)
            List of patterns to check.
        :param target: (string)
            Full path to target file.
        :return: (string)
            Full path to source file or ``None``.
        """
        # Initialize
        if media_type not in ('image', 'audio', 'video') or not media_id \
                or not patterns:
            return
        extensions = tuple(self._processor.config_list(
            'Input', '%s.ext' % media_type, MEDIA_EXT[media_type]))
        ext = splitext(target)[1][1:]
        extensions = ext in extensions and ((ext,) + extensions) or extensions
        resources = [join(self._processor.build.data_path, k) for k in
                     self._processor.build.pack['resources'] +
                     self._processor.build.processing['resources']]

        # Look for file in search patterns
        for pattern in [k for k in patterns if isabs(k)]:
            name = self._find_media_extension(extensions, pattern)
            if name is not None:
                return name
            patterns.remove(pattern)

        # Look for the file in resource files
        for resource in [k for k in resources if isfile(k)]:
            name, ext = splitext(basename(resource))
            if name == media_id and ext[1:] in extensions:
                return resource
            resources.remove(resource)

        # Look for the file in resource directories
        done = set()
        for resource in resources:
            for path, dirs, name in walk(resource):
                for name in dirs:
                    if name in EXCLUDED_FILES or '~' in name:
                        dirs.remove(name)
                if path in done:
                    continue
                done.add(path)
                for pattern in patterns:
                    name = self._find_media_extension(
                        extensions, join(path, pattern))
                    if name is not None:
                        return name
                    name = normpath(dirname(join(path, pattern)))
                    done.add(name)

    # -------------------------------------------------------------------------
    @classmethod
    def _find_media_extension(cls, extensions, absolute_pattern):
        """Look for the right extension for a media.

        :param extensions: (list)
            List of possible extensions.
        :param absolute_pattern: (string)
            Absolute pattern to build file name.
        :return: (string)
            The absolute path or ``None``.
        """
        for ext in '{ext}' in absolute_pattern and extensions or '-':
            name = absolute_pattern.format(ext=ext)
            if isfile(name):
                return normpath(name)

    # -------------------------------------------------------------------------
    def _get_in_attic(self, config, media_id, source, target):
        """Try to retrieve the media from the attic.

        :param config: (class:`ConfigParser.ConfigParser` instance)
            Current configuration object.
        :param media_id: (string)
            Media ID.
        :param source: (string)
            Full path to source file.
        :param target: (string)
            Full path to target file.
        :return: (boolean)
        """
        if self._processor.build.processing['variables'].get('force'):
            return False

        dependencies = config_get(config, 'Target', 'dependencies', '')\
            .format(id=media_id, source=source, sourcepath=dirname(source),
                    target=target, targetpath=dirname(target))
        dependencies = dependencies \
            and [k.strip() for k in dependencies.split(',')] or []

        relations = config_get(config, 'Target', 'relations', '')\
            .format(id=media_id, target=target, targetpath=dirname(target))
        relations = relations \
            and [k.strip() for k in relations.split(',')] or None

        return self._processor.build.get_in_attic(
            target, dependencies, relations)

    # -------------------------------------------------------------------------
    @classmethod
    def _bin(cls):
        """Return absolute path to PubliForge binary directory."""
        return \
            'VIRTUAL_ENV' in environ and join(environ['VIRTUAL_ENV'], 'bin') \
            or dirname(sys.executable)

    # -------------------------------------------------------------------------
    @classmethod
    def _rename_ini(cls, ini_file, done_tag):
        """Rename INI file after processing."""
        rename(
            ini_file,
            join(dirname(ini_file), '%s_%s' % (done_tag, basename(ini_file))))
