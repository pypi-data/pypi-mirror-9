#!/usr/bin/env python
# $Id: pfbuild.py d17160cbf54f 2015/02/09 10:53:37 Patrick $
"""Console script to execute a processing."""

import logging
from argparse import ArgumentParser
from os.path import exists, join, abspath, dirname, expanduser, relpath, isdir
from lxml import etree
from locale import getdefaultlocale
from textwrap import fill
from getpass import getuser
import re
import mimetypes

from ..lib.utils import _, localizer, copy_content
from ..lib.xml import load, local_text
from ..lib.build.agent import AgentBuildManager


__credits__ = '(c) Prismallia http://www.prismallia.fr, 2014'


LOG = logging.getLogger(__name__)


# =============================================================================
def main():
    """Main function."""
    # Parse arguments
    parser = ArgumentParser(description='Execute a processing.')
    parser.add_argument('build_file', help='Build file')
    parser.add_argument('files', nargs='*', help='optional files to process')
    parser.add_argument(
        '--list-processors', dest='list_processors',
        help='list available processors', action='store_true')
    parser.add_argument(
        '--list-variables', dest='list_variables', help='list variable values',
        action='store_true')
    parser.add_argument(
        '--show-variables', dest='show_variables',
        help='show variable parameters and values', action='store_true')
    parser.add_argument(
        '--processor-root', dest='processor_root', help='processor path')
    parser.add_argument(
        '--storage-root', dest='storage_root', help='storage path')
    parser.add_argument('--build-root', dest='build_root', help='build path')
    parser.add_argument('--build-id', dest='build_id', help='build ID')
    parser.add_argument(
        '--recursive', dest='recursive', help='recursive parsing',
        action='store_true')
    parser.add_argument('--output', dest='output', help='output directory')
    parser.add_argument(
        '--log-level', dest='log_level', help='log level', default='INFO',
        choices=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'))
    parser.add_argument('--log-file', dest='log_file', help='log file')
    args = parser.parse_args()
    output = args.output and expanduser(args.output) or None
    if not exists(args.build_file) or (output and not isdir(output)):
        parser.print_usage()
        return

    # Initialize log
    logformat = '%(asctime)s %(levelname)-8s %(message)s'
    if args.log_file:
        logging.basicConfig(
            filename=expanduser(args.log_file), filemode='w',
            level=args.log_level, format=logformat)
    else:
        logging.basicConfig(level=args.log_level, format=logformat)

    # Build
    BuildLauncher(args, output).start(args.build_file, args.files)


# =============================================================================
class BuildLauncher(object):
    """Class to launch a build on command-line."""

    # -------------------------------------------------------------------------
    def __init__(self, args, output=None):
        """Constructor method."""
        self._args = args
        self._output = output
        self._relaxngs = {
            'publiforge':
            join(dirname(__file__), '..', 'RelaxNG', 'publiforge.rng')}
        self._processor = None
        mimetypes.init((join(
            dirname(__file__), '..', 'Static', 'Images', 'MimeTypes',
            'mime.types'),))

    # -------------------------------------------------------------------------
    def start(self, build_file, files):
        """Start build.

        :param build_file: (string)
             Path to build XML file.
        :param files: (list)
             List of files on command-line.
        :return: (:class:`~.lib.build.agent.AgentBuild` instance or ``None``)
        """
        # Load build file
        build_tree = load(build_file, self._relaxngs)
        if isinstance(build_tree, basestring):
            LOG.critical(self._translate(build_tree))
            return

        # Read settings
        settings = self._read_settings(build_file, build_tree)
        if settings is None:
            return

        # Create agent
        build_manager = AgentBuildManager(settings)
        build_manager.processor_list()
        if self._args.processor_root:
            build_manager.add_processors(expanduser(self._args.processor_root))

        # Read processing & pack
        processing = self._read_processing(settings, build_manager, build_tree)
        pack = self._read_pack(settings, build_tree, files)
        if processing is None or pack is None \
                or self._list_processors(build_manager) \
                or self._display_variables(processing):
            return

        # Create a build and start it
        # pylint: disable = locally-disabled, no-member
        build_id = self._args.build_id  \
            or build_tree.find('build').get('id')
        context = {
            'user_id': 0, 'login': getuser(), 'lang': getdefaultlocale()[0],
            'name': getuser(), 'local': True}
        build = build_manager.start_build(build_id, context, processing, pack)

        # Check the result
        if build.result['status'] != 'a_end':
            return build
        if 'a_error' in [k[1] for k in build.result['log']]:
            LOG.critical(self._translate(_('error occurred')))
            return build

        # Display values
        if 'values' in build.result:
            for value in build.result['values']:
                LOG.info(self._translate(
                    _('Value = ${v}', {'v': value})))

        # Copy and display files
        if 'files' in build.result:
            if self._output:
                copy_content(join(build.path, 'Output'), self._output)
            for name in build.result['files']:
                name = self._output and join(self._output, name) \
                    or join(build.path, 'Output', name)
                LOG.info(self._translate(_('File = ${n}', {'n': name})))

        return build

    # -------------------------------------------------------------------------
    def _list_processors(self, build_manager):
        """List available processors.

        :param build_manager: (:class:`~.lib.build.agent.AgentBuildManager`
            instance) Current build_manager objet.
        :return: (boolean)
            ``True`` if processors have been listed.
        """
        if not self._args.list_processors:
            return False

        print '=' * 80
        print u'{0:^80}'.format(self._translate(_('Processor list')))
        print '=' * 80

        lang = getdefaultlocale()[0]
        for processor_id in build_manager.processor_list()[0]:
            tree = load(join(build_manager.processor_path(processor_id),
                             'processor.xml'), self._relaxngs)
            if isinstance(tree, basestring):
                print u'[{0:<16}] !!! {1:}'.format(
                    processor_id, self._translate(tree))
                continue

            print u'[{0:<16}] {1:}'.format(
                processor_id, local_text(tree, 'processor/label', lang=lang))

        return True

    # -------------------------------------------------------------------------
    def _display_variables(self, processing):
        """Display variable values and contraints.

        :param processing: (dictionary)
            Processing dictionary.
        :return: (boolean)
            ``True`` if variables have been displayed.
        """
        if not self._args.list_variables and not self._args.show_variables:
            return False

        # pylint: disable = locally-disabled, no-member
        fmt = u'  | {0:<11} : {1:}'
        lang = getdefaultlocale()[0]
        variables = processing['variables']
        for group in self._processor.find('processor/variables')\
                .iterchildren(tag=etree.Element):
            print '=' * 80
            print u'{0:^80}'.format(local_text(group, 'label', lang=lang))
            print '=' * 80
            if self._args.show_variables \
                    and group.find('description') is not None:
                print self._format_description(lang, group)
                print '-' * 80

            for var in group.findall('var'):
                name = var.get('name')
                label = local_text(var, 'label', lang=lang, default=name)
                var_type = var.get('type')
                value = variables.get(name, '')
                print u'{0:} = {1:}'.format(label, value)
                if not self._args.show_variables:
                    continue
                print '  v'
                if label != name:
                    print fmt.format(self._translate(_('Name')), name)
                if var.findtext('default') is not None:
                    print fmt.format(
                        self._translate(_('Default')),
                        var.findtext('default').strip())
                print fmt.format(self._translate(_('Type')), var_type)
                if var_type == 'regex':
                    print fmt.format(
                        self._translate(_('Pattern')),
                        var.findtext('pattern').strip())
                elif var_type == 'select':
                    print fmt.format(
                        self._translate(_('Options')),
                        ', '.join(['[%s] %s' % (k.get('value', k.text), k.text)
                                   for k in var.findall('option')]))
                if var.find('description') is not None:
                    print fmt.format(
                        self._translate(_('Description')),
                        self._format_description(lang, var, 18))
                print

        return True

    # -------------------------------------------------------------------------
    def _read_settings(self, build_file, build_tree):
        """Read settings from ``build_tree``.

        :param build_file: (string)
             Path to build XML file.
        :param build_tree: (etree.ElementTree)
            XML build tree.
        :return: (dictionary)
             A settings dictionary.
        """
        settings = {}
        element = build_tree.find('build/settings')
        for child in element.iterchildren(tag=etree.Element):
            key = child.get('key')
            if '.root' in key:
                settings[key] = ' '.join([
                    abspath(join(dirname(build_file), k))
                    for k in child.text.split()])
            else:
                settings[key] = child.text.strip()

        if self._args.storage_root:
            settings['storage.root'] = \
                expanduser(self._args.storage_root)
        if self._args.build_root:
            settings['build.root'] = expanduser(self._args.build_root)

        if not settings['build.root']:
            LOG.critical(
                self._translate(_('Must have a directory for builds.')))
        if 'processor.list' not in settings:
            settings['processor.list'] = '*'

        return settings

    # -------------------------------------------------------------------------
    def _read_processing(self, settings, build_manager, build_tree):
        """Load processing structure from ``build_tree``.

        :param settings: (dictionary)
             Settings.
        :param build_manager: (:class:`~.lib.build.agent.AgentBuildManager`
            instance) Current build_manager objet.
        :param build_tree: (etree.ElementTree)
            XML build tree.
        :return: (dictionary)
             A processing structure or ``None`` if fails.
        """
        # Main structure
        root_elt = build_tree.find('build/processing')
        processing = {'processor_id': root_elt.findtext('processor').strip()}

        # Load processor
        self._processor = build_manager.processor_path(
            processing['processor_id'])
        if self._processor is None:
            LOG.critical(self._translate(_(
                'Unknown processor ${p}.', {'p': processing['processor_id']})))
            return
        self._processor = load(
            join(self._processor, 'processor.xml'), self._relaxngs,
            build_manager.processor_xml(processing['processor_id']))
        if isinstance(self._processor, basestring):
            LOG.critical(self._translate(self._processor))
            return

        # Variables
        processing['variables'] = self._read_variables(build_tree)
        if processing['variables'] is None:
            return

        # Resource files
        path = settings['storage.root']
        processing['resources'] = self._read_file_set(
            path, build_tree.find('build/processing/resources'))
        if processing['resources'] is None:
            return

        # Template files
        processing['templates'] = self._read_file_set(
            path, build_tree.find('build/processing/templates'))
        if processing['templates'] is None:
            return

        return processing

    # -------------------------------------------------------------------------
    def _read_pack(self, settings, build_tree, files):
        """Load pack structure from ``build_tree``.

        :param settings: (dictionary)
             Settings.
        :param build_tree: (etree.ElementTree)
            XML build tree.
        :param files: (list)
             List of files on command-line to process.
        :return: (dictionary)
             A pack structure or ``None`` if fails.
        """
        # Main structure
        pack = {'recursive': '0'}
        element = build_tree.find('build/pack')
        if element is not None and element.get('recursive') == 'true'\
                or self._args.recursive:
            pack['recursive'] = '1'

        # Files
        path = settings['storage.root']
        pack['files'] = self._read_file_set(
            path, build_tree.find('build/pack/files'))
        if pack['files'] is None:
            return

        # Files from command-line
        for name in files:
            name = expanduser(name)
            if not exists(name):
                LOG.critical(self._translate(
                    _('Unknown file "${n}".', {'n': name})))
                return
            pack['files'].append(relpath(name, path).decode('utf8'))

        # Resource files
        pack['resources'] = self._read_file_set(
            path, build_tree.find('build/pack/resources'))
        if pack['resources'] is None:
            return

        # Template files
        pack['templates'] = self._read_file_set(
            path, build_tree.find('build/pack/templates'))
        if pack['templates'] is None:
            return

        return pack

    # -------------------------------------------------------------------------
    def _read_variables(self, build_tree):
        """Read variable definitions in processor tree and fill ``variables``
        dictionary.

        :param build_tree: (:class:`lxml.etree.ElementTree`)
             Build element tree.
        :return: (dictionary)
             Variable dictionary.
        """
        # pylint: disable = locally-disabled, E1103
        variables = {}
        var = build_tree.find('build/processing/variables')
        values = {} if var is None else dict([
            (k.get('name'), k.text is not None and k.text.strip() or '')
            for k in var.findall('var')])

        for var in self._processor.findall('processor/variables/group/var'):
            name = var.get('name')
            error = self._translate(_('${v}: bad value.', {'v': name}))
            value = values[name] if name in values \
                else var.findtext('default') is not None \
                and var.findtext('default').strip() or ''

            if var.get('type') == 'boolean':
                if value not in ('true', 'false', '1', '0', ''):
                    LOG.critical(error)
                    return
                value = bool(value == 'true')
            elif var.get('type') == 'integer':
                if not value.isdigit():
                    LOG.critical(error)
                    return
                value = int(value)
            elif var.get('type') == 'select':
                if value not in [k.get('value') or k.text
                                 for k in var.findall('option')]:
                    LOG.critical(error)
                    return
                value = int(value) if value.isdigit() else value
            elif var.get('type') == 'regex':
                if not re.match('^%s$' % var.findtext('pattern').strip(),
                                value):
                    LOG.critical(error)
                    return
            variables[name] = value

        return variables

    # -------------------------------------------------------------------------
    def _read_file_set(self, storage_root, element):
        """Read files from ``element``.

        :param storage_root: (string)
            Absolute root path to storages.
        :param element: (etree.Element object)
            ``templates`` XML element.
        :return: (list)
            A list of tuples such as ``(<input_file>, <output_path>)`` or
            ``None`` if fails.
        """
        set_list = []
        if element is None:
            return set_list

        for child in element.iterchildren(tag=etree.Element):
            name = child.text.strip()
            if not exists(join(storage_root, name)):
                LOG.critical(self._translate(
                    _('Unknown file "${n}".', {'n': name})))
                return
            if child.get('to'):
                set_list.append((name, child.get('to')))
            else:
                set_list.append(name)

        return set_list

    # -------------------------------------------------------------------------
    @classmethod
    def _format_description(cls, lang, root_elt, indent=0, width=80):
        """Return formatted description text.

        :param lang: (string)
            Preferred language.
        :param root_elt: (:class:`lxml.etree.Element` instance)
            Description element parent.
        :param indent: (integer, default=0)
            Indent value.
        :param width: (integer, default=80)
            Text width.
        :return: string
        """
        text = local_text(root_elt, 'description', lang=lang)
        if not indent and ' --' in text:
            return '\n'.join([fill(k.strip(), width, subsequent_indent='    ')
                              for k in text.split(' --')])

        subsequent_indent = '  |' + ' ' * (indent - 3)
        return fill(text, width, initial_indent=' ' * indent,
                    subsequent_indent=subsequent_indent).strip()

    # -------------------------------------------------------------------------
    @classmethod
    def _translate(cls, text):
        """Return ``text`` translated.

        :param text: (string)
            Text to translate.
        """
        return localizer(getdefaultlocale()[0]).translate(text)


# =============================================================================
if __name__ == '__main__':
    main()
