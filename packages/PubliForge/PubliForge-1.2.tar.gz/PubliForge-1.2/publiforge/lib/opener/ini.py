# $Id: ini.py 7a61ebd138f5 2014/08/24 14:53:02 Patrick $
"""INI configuration file opener."""

from os.path import join
from ConfigParser import RawConfigParser, ParsingError
from webhelpers2.html import literal
from cStringIO import StringIO
from lxml import etree
from copy import deepcopy
import re

from pyramid.i18n import get_localizer

from ..utils import _
from ..viewutils import variable_input
from ..form import Form
from ..xml import XML_NS, PUBLIFORGE_RNG_VERSION, local_text
from . import MAIN_ROUTE, Opener as OpenerBase


# =============================================================================
class Opener(OpenerBase):
    """Class to operate on configuration INI files."""
    # pylint: disable = locally-disabled, too-many-public-methods

    _config_file = 'ini.ini'

    # -------------------------------------------------------------------------
    @classmethod
    def can_render(cls):
        """Return ``True`` if it can produce a rendering.

        See parent method :meth:`~.lib.opener.Opener.can_render`.
        """
        return True

    # -------------------------------------------------------------------------
    def render(self, request, storage, path, content=None, native=None):
        """Literal XHTML to display INI file rendering.

        See parent method :meth:`~.lib.opener.Opener.render`.
        """
        # Load environment
        if not self.install_environment(request):
            return ''
        ini = native or self._load_native(request, storage, path, content)
        if ini is None:
            return ''
        variables = self._variable_structure(ini)

        # Create XHTML structure
        translate = get_localizer(request).translate
        html = '<table class="list">\n<thead>\n'\
            '<tr><th colspan="3">%s</th><th>%s</th></tr>\n</thead>\n'\
            % (translate(_('Key')), translate(_('Value')))
        for group_elt in variables.findall('variables/group'):
            html += '<tbody class="group">\n'\
                '<tr><th colspan="4">%s</th></tr>\n' \
                % local_text(group_elt, 'label', request)
            for var_elt in group_elt.findall('var'):
                default = var_elt.findtext('default')
                if default:
                    default = default.replace('&', '&amp;')\
                        .replace('<', '&lt;').replace('>', '&gt;')
                    html += '<tr><td class="checkbox"></td>'\
                            '<td class="key">%s</td><td>=</td>' \
                            '<td class="value">%s</td></tr>\n' \
                            % (local_text(var_elt, 'label', request), default)
            html += '</tbody>\n'
        html += '</table>\n'

        return literal(html)

    # -------------------------------------------------------------------------
    def can_edit(self):
        """Return ``True`` if it can produce an editor.

        :return: (boolean)
        """
        return True

    # -------------------------------------------------------------------------
    def edit(self, request, action, storage, path, content=None):
        """Literal XHTML to edit file.

        See parent method :meth:`~.lib.opener.OpenerBase.edit`.
        """
        # Load environment
        if not self.install_environment(request):
            return Form(request), '', content
        ini = self._get_native(
            request, storage, path, content, request.params)
        if ini is None:
            return Form(request), '', None
        variables = self._variable_structure(ini)

        # Create form
        form = self._edit_form(request, storage, variables, True)
        if action == 'sav!':
            form.validate()

        # Create XHTML structure
        translate = get_localizer(request).translate
        html = literal(
            '<table class="list tableToolTip">\n<thead>\n'
            '<tr><th colspan="3">%s</th><th colspan="2">%s</th></tr>\n'
            '</thead>\n' % (translate(_('Key')), translate(_('Value'))))
        for group_elt in variables.findall('variables/group'):
            html += literal(
                '<tbody class="group">\n'
                '<tr><th colspan="5">%s</th></tr>\n'
                % local_text(group_elt, 'label', request))
            for var_elt in group_elt.findall('var'):
                html += literal(
                    '<tr><td class="checkbox"></td><td class="key">%s</td>'
                    '<td>=</td>' % local_text(var_elt, 'label', request))
                html += var_elt.find('description') is None \
                    and literal('<td class="value" colspan="2">') \
                    or literal('<td class="value">')
                html += variable_input(
                    form, var_elt.get('name'), var_elt.get('type'), var_elt)
                html += literal('</td>')
                if var_elt.find('description') is not None:
                    html += literal(
                        '<td class="checkbox">'
                        '<input type="image" name="des!%s" class="toolTip"'
                        ' src="%s/Images/action_help_one.png"/></td>'
                        % (var_elt.get('name'), MAIN_ROUTE))
                html += literal('</tr>\n')
            html += literal('</tbody>\n')
        html += literal('</table>\n')

        return form, html, ini

    # -------------------------------------------------------------------------
    def _load_native(self, request, storage, path, content=None):
        """Load a :class:`ConfigParser.RawConfigParser` object.

        See parent method :meth:`~.lib.opener.Opener._load_native`.
        """
        if content is not None:
            return self._content2native(request, content)

        ini = RawConfigParser()
        ini.optionxform = str
        try:
            ini.read(join(
                request.registry.settings['storage.root'],
                storage['storage_id'], path))
        except ParsingError as error:
            request.session.flash(error, 'alert')
            return
        return ini

    # -------------------------------------------------------------------------
    @classmethod
    def _content2native(cls, request, content):
        """Transform a string into a :class:`ConfigParser.RawConfigParser`
        object and validate it.

        See parent method :meth:`~.lib.opener.Opener._content2native`.
        """
        ini = RawConfigParser()
        ini.optionxform = str
        content = StringIO(content)
        try:
            ini.readfp(content)
        except ParsingError as error:
            content.close()
            request.session.flash(error, 'alert')
            return
        content.close()
        return ini

    # -------------------------------------------------------------------------
    @classmethod
    def _native2content(cls, request, native):
        """Transform a :class:`ConfigParser.RawConfigParser` object into a
        string.

        See parent method :meth:`~.lib.opener.Opener._native2content`.
        """
        if native is None:
            return ''
        content = StringIO()
        native.write(content)
        native = content.getvalue()
        content.close()
        content = re.sub(
            r'(\[[A-Z][a-z0-9_-]+\])', r'# %s\n\1' % ('=' * 77), native)
        return content

    # -------------------------------------------------------------------------
    def _values2native(self, request, storage, path, content, values):
        """Transform a dictionary of values into a
        :class:`ConfigParser.RawConfigParser` object and validate it.

        See parent method :meth:`~.lib.opener.Opener._values2native`.
        """
        ini = self._load_native(request, storage, path, content)
        if ini is None:
            return None, False
        variables = self._variable_structure(ini)
        for group_elt in variables.findall('variables/group'):
            section = group_elt.get('name')
            for var_elt in group_elt.findall('var'):
                option = var_elt.get('name')[len(section) + 1:]
                name = '%s:%s' % (section, option)
                if not values.get(name) \
                   and ini.has_option(section, option):
                    ini.remove_option(section, option)
                    continue
                if not values.get(name):
                    continue
                if isinstance(values[name], bool) and values[name]:
                    ini.set(section, option, 'true')
                elif isinstance(values[name], int):
                    ini.set(section, option, str(values[name]))
                elif values[name].strip():
                    ini.set(section, option,
                            values[name].strip().encode('utf8'))
        return ini, True

    # -------------------------------------------------------------------------
    def _variable_structure(self, ini):
        """Create a XML variable structure with a description of each option.

        :param ini: (:class:`ConfigParser.RawConfigParser` instance)
            Current configuration.
         :return: (:class:`lxml.etree.ElementTree` instance)
        """
        # Create from INI structure
        variables = etree.Element(
            'publiforge', version=PUBLIFORGE_RNG_VERSION)
        etree.SubElement(variables, 'variables')
        root = variables[0]
        for section in ini.sections():
            group_elt = etree.SubElement(root, 'group', name=section)
            elt = etree.SubElement(group_elt, 'label')
            elt.set('%slang' % XML_NS, 'en')
            elt.text = section
            for option in ini.options(section):
                name = '%s:%s' % (section, option)
                var_elt = etree.SubElement(
                    group_elt, 'var', name=name, type='string')
                default = ini.get(section, option)
                if default:
                    elt = etree.SubElement(var_elt, 'default')
                    elt.text = default.decode('utf8')
                elt = etree.SubElement(var_elt, 'label')
                elt.set('%slang' % XML_NS, 'en')
                elt.text = option

        # Complete with variables XML
        # pylint: disable = locally-disabled, maybe-no-member
        self._load_variables_xml()
        if self._variables_xml:
            for frame_group_elt in self._variables_xml\
                    .getroot()[0].findall('group'):
                group_elt = root.xpath(
                    "group[@name='%s']" % frame_group_elt.get('name'))
                if len(group_elt):
                    group_elt = group_elt[0]
                else:
                    group_elt = etree.SubElement(
                        root, 'group', name=frame_group_elt.get('name'))
                self._update_group_labels(frame_group_elt, group_elt)
                for frame_var_elt in frame_group_elt.findall('var'):
                    name = '%s:%s' % (
                        frame_group_elt.get('name'), frame_var_elt.get('name'))
                    var_elt = group_elt.xpath("var[@name='%s']" % name)
                    if len(var_elt):
                        var_elt = var_elt[0]
                    else:
                        var_elt = etree.SubElement(group_elt, 'var', name=name)
                    self._update_var(frame_var_elt, var_elt, name)

        return variables

    # -------------------------------------------------------------------------
    @classmethod
    def _update_group_labels(cls, frame_elt, group_elt):
        """Update or create labels for element ``group_elt`` with labels of
        ``frame_elt``.

        :param frame_elt: (:class:`lxml.etree.Element` instance)
        :param group_elt: (:class:`lxml.etree.Element` instance)
        """
        # Labels
        for label_elt in frame_elt.findall('label'):
            elt = group_elt.xpath(
                "label[@xml:lang='%s']"
                % label_elt.get('%slang' % XML_NS))
            if len(elt):
                elt[0].text = label_elt.text
            else:
                elt = etree.Element('label')
                elt.set('%slang' % XML_NS, label_elt.get('%slang' % XML_NS))
                elt.text = label_elt.text
                group_elt.insert(0, elt)

    # -------------------------------------------------------------------------
    @classmethod
    def _update_var(cls, frame_elt, var_elt, name):
        """Update ``var_elt`` with ``frame_elt``.

        :param frame_elt: (:class:`lxml.etree.Element` instance)
        :param var_elt: (:class:`lxml.etree.Element` instance)
        :param name: (string)
        """
        new_var_elt = deepcopy(frame_elt)
        new_var_elt.set('name', name)
        default = var_elt.findtext('default')
        if default:
            elt = new_var_elt.find('default')
            if elt is None:
                elt = etree.Element('default')
                new_var_elt.insert(0, elt)
            elt.text = default
        var_elt.getparent().replace(var_elt, new_var_elt)
