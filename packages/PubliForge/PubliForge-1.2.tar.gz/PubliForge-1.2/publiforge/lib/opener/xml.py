# $Id: xml.py 7981fd623a54 2015/02/21 08:15:22 Patrick $
"""XML file opener."""

from os import listdir
from os.path import join, exists, basename, dirname, splitext, isfile, isdir
from os.path import relpath, isabs
from lxml import etree
from webhelpers2.html import literal
import re

from pyramid.asset import abspath_from_asset_spec
from pyramid.i18n import get_localizer

from ..utils import _, make_id, config_get_list, load_regex
from ..viewutils import variable_input
from ..form import Form
from ..xml import PF_NAMESPACE, load
from ..xml import xpath_camel_case, xpath_make_id, xpath_relpath
from . import MAIN_ROUTE, OPENER_ROUTE, Opener as OpenerBase


MEDIA_EXTENSIONS = {
    'image': ('png', 'jpg', 'jpeg', 'gif', 'svg'),
    'audio': ('ogg', 'wav', 'mp3'),
    'video': ('ogv', 'webm', 'mp4')}
MEDIA_SEARCH = {
    'image': ('Images/{id}.{ext}', 'Thumbnails/{id}.{ext}'),
    'audio': ('Audios/{id}.{ext}',),
    'video': ('Videos/{id}.{ext}',)}
MEDIA_REGEX = {
    'image': r'(src|poster)="%s\/Images\/notfound.jpg#([^"]+)' % MAIN_ROUTE,
    'audio': r'(src|href)="\/media\/audios\/([^"]+)',
    'video': r'(src|href)="\/media\/videos\/([^"]+)'
}


# =============================================================================
class Opener(OpenerBase):
    """Class to operate on XML files."""
    # pylint: disable = locally-disabled, too-many-public-methods

    _config_file = 'xml.ini'

    # -------------------------------------------------------------------------
    def __init__(self, opener_manager, opener_id, opener_xml):
        """Constructor method.

        See parent method :meth:`~.lib.opener.Opener.__init__`.
        """
        super(Opener, self).__init__(opener_manager, opener_id, opener_xml)
        self._relaxngs = None
        self._xslt = {}
        self._regex = {}

        # XSL namespace with Python fucntions
        namespace = etree.FunctionNamespace(PF_NAMESPACE)
        namespace['camel_case'] = xpath_camel_case
        namespace['make_id'] = xpath_make_id
        namespace['relpath'] = xpath_relpath

    # -------------------------------------------------------------------------
    def can_render(self):
        """Return ``True`` if it can produce a rendering.

        :return: (boolean)
        """
        return bool(self._config_get('Render', 'Xsl'))

    # -------------------------------------------------------------------------
    def render(self, request, storage, path, content=None, native=None):
        """Literal XHTML to display XML file rendering.

        See parent method :meth:`~.lib.opener.Opener.render`.
        """
        # Load environment and XML file
        if not self.install_environment(request):
            return ''
        xml = native or self._load_native(request, storage, path, content)
        if xml is None:
            return ''

        # XSL transformation
        if not self._load_xsl(request, 'render', 'Render', 'xsl'):
            return ''
        try:
            html = self._xslt['render'](xml, **self._xsl_params(path))
        except etree.XSLTApplyError as error:
            request.session.flash(error, 'alert')
            return ''

        # Fix media source
        html = self._fix_media(request, 'render', storage, path, unicode(html))

        return literal(html)

    # -------------------------------------------------------------------------
    def can_write(self):
        """Return ``True`` if it can simply modify the file.

        See parent method :meth:`~.lib.opener.Opener.can_write`.
        """
        return bool(self._config_get('Write', 'css'))

    # -------------------------------------------------------------------------
    def can_edit(self):
        """Return ``True`` if it can produce an editor.

        :return: (boolean)
        """
        return self._opener_xml.find('opener/variables') is not None \
            and bool(self._config_get('Edit', 'xsl')) \
            and bool(self._config_get('Edit', 'save.xsl')) \
            and bool(self._config_get('Edit', 'save.regex'))

    # -------------------------------------------------------------------------
    def edit(self, request, action, storage, path, content=None):
        """Literal XHTML to edit file.

        See parent method :meth:`~.lib.opener.Opener.edit`.
        """
        # Load environment
        if not self.install_environment(request)\
           or not self._load_xsl(request, 'edit', 'Edit', 'xsl') \
           or not self._load_xsl(request, 'save', 'Edit', 'save.xsl') \
           or not self._load_regex(request, 'save', 'Edit', 'save.regex'):
            return Form(request), '', None
        xml = self._get_native(
            request, storage, path, content, request.params)
        if xml is None:
            return Form(request), '', None
        try:
            variables = self._xslt['edit'](
                xml, **self._xsl_params(path, 'variables'))
        except etree.XSLTApplyError as error:
            request.session.flash(error, 'alert')
            return Form(request), '', xml

        # Create form
        form = self._edit_form(request, storage, variables)
        if action == 'sav!':
            form.validate()

        # Create XHTML structure
        try:
            html = self._xslt['edit'](xml, **self._xsl_params(path, 'html'))
        except etree.XSLTApplyError as error:
            request.session.flash(error, 'alert')
            return Form(request), '', xml
        html = unicode(html)
        for var in variables.findall('variables/group/var'):
            field = '%s%s' % (
                variable_input(form, var.get('name'), var.get('type'), var),
                self._variable_error(request, form, var))
            html = html.replace('__%s__' % var.get('name'), field)

        return form, literal(html), xml

    # -------------------------------------------------------------------------
    def find_media(self, filename, media_type, media_id, patterns=None,
                   extensions=None):
        """Return the absolute path to the media ``media_id``.

        See parent method :meth:`~.lib.opener.Opener.find_media`.
        """
        if not media_id or media_type not in ('image', 'audio', 'video'):
            return
        if patterns is None:
            patterns = config_get_list(
                self._config, 'Render', '%s.search' % media_type,
                MEDIA_SEARCH[media_type])
        if extensions is None:
            extensions = config_get_list(
                self._config, 'Render', '%s.ext' % media_type,
                MEDIA_EXTENSIONS[media_type])
        base = dirname(filename)

        for pattern in patterns:
            for ext in '{ext}' in pattern and extensions or '-':
                name = pattern.format(id=media_id, ext=ext)
                if not isabs(name):
                    name = join(base, name)
                if isfile(name):
                    return name

    # -------------------------------------------------------------------------
    def resources_dirs(self, filename, media_type):
        """Return the list of resource directories.

        See parent method :meth:`~.lib.opener.Opener.resources_dirs`.
        """
        if media_type not in ('image', 'audio', 'video'):
            return []
        root = dirname(filename)
        patterns = config_get_list(
            self._config, 'Render', '%s.search' % media_type,
            MEDIA_SEARCH[media_type])
        dirs = []
        for pattern in patterns:
            pattern = isabs(pattern) and dirname(pattern) \
                or dirname(join(root, pattern))
            if isdir(pattern):
                dirs.append(pattern)

        return dirs

    # -------------------------------------------------------------------------
    def resources_files(self, path, media_type, media_only):
        """Return the list of media files of ``path`` directory.

        See parent method :meth:`~.lib.opener.Opener.resources_files`.
        """
        if media_type not in ('image', 'audio', 'video'):
            return []
        extensions = config_get_list(
            self._config, 'Render', '%s.ext' % media_type,
            MEDIA_EXTENSIONS[media_type])
        files = []
        for name in listdir(path):
            if not media_only or splitext(name)[1][1:] in extensions:
                files.append(name)
        return sorted(files)

    # -------------------------------------------------------------------------
    def _variable_error(self, request, form, var):
        """Return a potential error on the content of the variable.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param form: (:class:`~.lib.form.Form` instance)
            Current form.
        :param var: (:class:`lxml.etree.Element` instance)
            DOM element of the variable.
        :return: (string)
        """
        # Colander error
        name = var.get('name')
        if form.has_error(name):
            return literal(
                '<strong class="error">%s</strong>' % form.error(name))
        if name not in request.params or not request.params[name].strip():
            return ''

        # Relax NG error
        cast = self._config_get('Casts', var.get('cast', ''))
        if cast is None:
            return ''
        cast = cast.format(xml=request.params[name]).encode('utf8')
        cast = load('', self._relaxngs, cast)
        if isinstance(cast, basestring):
            return literal(
                '<strong class="error">%s</strong>' %
                get_localizer(request).translate(cast)
                .replace('<', '&lt;').replace('>', '&gt;'))
        return ''

    # -------------------------------------------------------------------------
    def _load_native(self, request, storage, path, content=None):
        """Load a :class:`lxml.etree.ElementTree` object.

        See parent method :meth:`~.lib.opener.Opener._load_native`.
        """
        if content is not None:
            return self._content2native(request, content)

        if not self._load_relaxngs(request):
            return
        filename = join(
            request.registry.settings['storage.root'], storage['storage_id'],
            path)
        xml = load(filename, self._relaxngs)
        if isinstance(xml, basestring):
            request.session.flash(xml, 'alert')
            return
        return xml

    # -------------------------------------------------------------------------
    def _content2native(self, request, content):
        """Transform a string into a :class:`lxml.etree.ElementTree` object
        and validate it.

        See parent method :meth:`~.lib.opener.Opener._content2native`.
        """
        if not self._load_relaxngs(request):
            return

        xml = load('', self._relaxngs and self._relaxngs or None, content)
        if isinstance(xml, basestring):
            request.session.flash(xml, 'alert')
            return
        return xml

    # -------------------------------------------------------------------------
    @classmethod
    def _native2content(cls, request, native):
        """Transform a :class:`lxml.etree.ElementTree` object into a string.

        See parent method :meth:`~.lib.opener.Opener._native2content`.
        """
        if native is None:
            return ''
        return etree.tostring(
            native, pretty_print=True, encoding='utf-8', xml_declaration=True)

    # -------------------------------------------------------------------------
    def _values2native(self, request, storage, path, content, values):
        """Transform a dictionary of values into a
        :class:`lxml.etree.ElementTree` object and validate it.

        See parent method :meth:`~.lib.opener.Opener._values2native`.
        """
        xml = self._load_native(request, storage, path, content)
        if xml is None \
           or not self._load_xsl(request, 'save', 'Edit', 'save.xsl'):
            return None, False
        try:
            data = self._xslt['save'](xml, **self._xsl_params(path))
        except etree.XSLTApplyError as error:
            request.session.flash(error, 'alert')
            return xml, False
        data = etree.tostring(data, encoding='utf-8')

        # Replace fields
        for name in values:
            if name not in ('_csrf', 'message', 'vcs_user', 'vcs_password') \
               and name[-2:] not in ('.x', '.y') and values[name] is not None:
                data = data.replace(
                    '__%s__' % name, isinstance(values[name], bool) and
                    str(values[name]) or
                    values[name].strip().encode('utf8'))
        self._load_regex(request, 'save', 'Edit', 'save.regex')
        data = data.decode('utf8')
        for regex in self._regex['save']:
            data = regex[0].sub(regex[1], data)
        data = data.encode('utf8')

        # Convert into an ElementTree
        native = load(path, self._relaxngs, data, noline=True)
        if not isinstance(native, basestring):
            return native, True
        request.session.flash(native, 'alert')
        native = load(path, data=data)
        return isinstance(native, basestring) and xml or native, False

    # -------------------------------------------------------------------------
    def _fix_media(self, request, mode, storage, path, html):
        """Fix image, audio and video source if possible.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param mode: ('render' or 'edit')
            Mode.
        :param storage: (dictionary)
            Storage dictionary.
        :param path: (string)
            Relative path to the file to fix.
        :param html: (string)
            HTML content to fix.
        :return: (string)
            Fixed HTML content
        """
        storage_root = request.registry.settings['storage.root']
        filename = join(storage_root, storage['storage_id'], path)
        mode = mode.capitalize()
        for media_type in ('image', 'audio', 'video'):
            patterns = config_get_list(
                self._config, mode, '%s.search' % media_type,
                MEDIA_SEARCH[media_type])
            extensions = config_get_list(
                self._config, mode, '%s.ext' % media_type,
                MEDIA_EXTENSIONS[media_type])
            if not patterns or not extensions:
                continue

            for regex in re.finditer(MEDIA_REGEX[media_type], html):
                name = self.find_media(
                    filename, media_type, regex.group(2), patterns, extensions)
                if name is not None:
                    name = relpath(name, storage_root)
                    name = request.route_path(
                        'file_download', storage_id=name.partition('/')[0],
                        path=name.partition('/')[2])
                    html = html.replace(
                        '%s"' % regex.group(0),
                        '%s="%s"' % (regex.group(1), name))
        return html

    # -------------------------------------------------------------------------
    def _load_relaxngs(self, request):
        """Load the Relax NG file into memory.

        :return: (boolean)
        """
        if self._relaxngs is not None \
           and self._manager.settings.get('opener.develop') != 'true':
            return True

        self._relaxngs = {}
        if not self._config_get('RelaxNG', 'here'):
            return True

        excluded = (
            'here', 'main_route', 'route', 'stgpath', 'lang', 'id', 'ext',
            'xml', 'image.ext', 'image.search', 'audio.ext', 'audio.search',
            'video.ext', 'video.search')
        for root, filename in self._config.items('RelaxNG'):
            if root in excluded:
                continue
            root = root.replace('|', ':')
            try:
                self._relaxngs[root] = etree.RelaxNG(etree.parse(filename))
            except (IOError, etree.XMLSyntaxError,
                    etree.RelaxNGParseError) as error:
                request.session.flash(error, 'alert')
                self._relaxngs = None
                return False
        return True

    # -------------------------------------------------------------------------
    def _load_xsl(self, request, name, section, option):
        """Load an XSL into memory.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param name: (string)
            Name of the asked XSL.
        :param section: (string)
            Section of the INI file for the XSL.
        :param option: (string)
            Option of the INI file for the XSL.
        :return: (boolean)
        """
        if name in self._xslt \
           and self._manager.settings.get('opener.develop') != 'true':
            return True

        xsl_file = self._config_get(section, option)
        if xsl_file is None:
            return False
        try:
            xslt = etree.XSLT(etree.parse(xsl_file))
        except (IOError, etree.XSLTParseError,
                etree.XMLSyntaxError) as error:
            request.session.flash(error, 'alert')
            return False
        self._xslt[name] = xslt
        return True

    # -------------------------------------------------------------------------
    def _xsl_params(self, filename, mode=None):
        """Create parameters for XLS transformation.

        :param filename: (string)
            Name of the XML file to transform
        :param mode: (``'variables'`` or ``'html'``, optional)
            Current mode for CSS.
        :return: (dictionary)
        """
        opener_route = '/' + OPENER_ROUTE % self.opener_id
        params = {
            'fid': '"%s"' % make_id(splitext(basename(filename))[0], 'token'),
            'main_route': '"%s/"' % MAIN_ROUTE,
            'route': '"%s/"' % opener_route}
        if self._opener_xml.find('opener/variables') is not None:
            params['variables'] = '"%s"' % join(
                self._path,
                self._opener_xml.findtext('opener/variables/group-file'))
        if mode is not None:
            params['mode'] = '"%s"' % mode
        return params

    # -------------------------------------------------------------------------
    def _load_regex(self, request, name, section, option):
        """Load a list of regular expressions into memory.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param name: (string)
            Name of the asked regular expression file.
        :param section: (string)
            Section of the INI file for the regex.
        :param option: (string)
            Option of the INI file for the regex.
        :return: (boolean)
        """
        if name in self._regex \
           and self._manager.settings.get('opener.develop') != 'true':
            return True

        self._regex[name] = []
        for regex_file in config_get_list(self._config, section, option, []):
            if not exists(abspath_from_asset_spec(regex_file)):
                request.session.flash(
                    _('Unknown file "${n}"', {'n': regex_file}), 'alert')
                self._regex[name] = tuple()
                return False
            self._regex[name] += load_regex(
                abspath_from_asset_spec(regex_file))

        self._regex[name] = tuple(self._regex[name])
        return True
