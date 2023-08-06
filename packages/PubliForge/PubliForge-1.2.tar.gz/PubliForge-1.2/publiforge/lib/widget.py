# $Id: widget.py 7981fd623a54 2015/02/21 08:15:22 Patrick $
# -*- coding: utf-8 -*-
"""Some various widgets."""

from urllib import urlencode
from string import Template
import re
from webhelpers2.html import literal, HTML, tags
from sqlalchemy import select
from sqlalchemy.orm.query import Query

from pyramid.i18n import get_localizer

from ..lib.utils import _, has_permission
from ..models import TRUE, DBSession
from ..models.users import PAGE_SIZE
from ..models.groups import GROUPS_USERS
from ..models.storages import Storage, StorageUser
from ..models.projects import Project, ProjectUser, ProjectGroup


# =============================================================================
def sortable_column(request, label, sort, current_sorting=None,
                    paging_id=None):
    """Output a header of column with `sort up` and `sort down` buttons.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param label: (string)
         Label of column.
    :param sort: (string)
         Sort criteria.
    :param current_sorting: (string, optional)
        Default current sorting.
    :param paging_id: (string, optional)
        Paging ID.
    :return: (literal HTML string)
    """
    img = '/Static/Images/sort_%s.png'
    current = request.params.get('sort') or current_sorting
    query_string = {}
    if request.GET:
        query_string.update(request.GET)
    if paging_id:
        query_string.update({'paging_id': paging_id})

    query_string['sort'] = '+%s' % sort
    url = request.current_route_path(_query=query_string)
    xhtml = '+%s' % sort == current and tags.image(img % 'down_off', 'Down')\
            or HTML.a(tags.image(img % 'down', 'Down'), href=url)

    query_string['sort'] = '-%s' % sort
    url = request.current_route_path(_query=query_string)
    xhtml += '-%s' % sort == current and tags.image(img % 'up_off', 'Up')\
             or HTML.a(tags.image(img % 'up', 'Up'), href=url)

    return literal('%s %s' % (label, xhtml))


# =============================================================================
class Breadcrumbs(object):
    """User breadcrumb trail, current title page and back URL management.

    This class uses session and stores its history in
    ``session['breadcrumbs']``. It is a list of crumbs. Each crumb is a tuple
    such as ``(<title>, <route_name>, <route_parts>)``
    """

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        self._request = request

    # -------------------------------------------------------------------------
    def current_title(self):
        """Title of current page."""
        session = self._request.session
        return \
            ('breadcrumbs' in session and len(session['breadcrumbs']) > 0 and
             session['breadcrumbs'][-1][0]) or ''

    # -------------------------------------------------------------------------
    def current_path(self):
        """Path of current page."""
        if 'breadcrumbs' not in self._request.session:
            return self._request.route_path('home')
        crumb = self._request.session['breadcrumbs'][-1]
        return self._request.route_path(crumb[1], **crumb[2])

    # -------------------------------------------------------------------------
    def trail(self):
        """Output XHTML breadcrumb trail."""
        if 'breadcrumbs' not in self._request.session \
           or len(self._request.session['breadcrumbs']) < 2:
            return literal('&nbsp;')

        translate = get_localizer(self._request).translate
        crumbs = []
        for crumb in self._request.session['breadcrumbs'][0:-1]:
            if crumb[1] is not None:
                crumbs.append(u'<a href="%s">%s</a>' % (
                    self._request.route_path(crumb[1], **crumb[2]),
                    translate(crumb[0])))
            else:
                crumbs.append(translate(crumb[0]))
        return literal(u' » '.join(crumbs))

    # -------------------------------------------------------------------------
    def back_title(self):
        """Output title of previous page."""
        if 'breadcrumbs' not in self._request.session \
           or len(self._request.session['breadcrumbs']) < 2:
            return _('home')
        return get_localizer(self._request).translate(
            self._request.session['breadcrumbs'][-2][0])

    # -------------------------------------------------------------------------
    def back_button(self):
        """A button to return to the previous page."""
        return literal(
            u'<a href="{0}" title="{1}">'
            '<img src="/Static/Images/back.png" alt="Back"/></a>'.format(
                self.back_path(), self.back_title()))

    # -------------------------------------------------------------------------
    def back_path(self):
        """Output the path of previous page."""
        if 'breadcrumbs' not in self._request.session \
           or len(self._request.session['breadcrumbs']) < 2:
            return self._request.route_path('home')
        crumb = self._request.session['breadcrumbs'][-2]
        return self._request.route_path(crumb[1], **crumb[2])

    # -------------------------------------------------------------------------
    def add(self, title, length=10, root_chunks=10, replace=None, anchor=None):
        """Add a crumb in breadcrumb trail.

        :param title: (string)
            Page title in breadcrumb trail.
        :param length: (int, default=10)
            Maximum crumb number. If 0, it keeps the current length.
        :param root_chunks: (int, default=10)
            Number of path chunks to compare to highlight menu item.
        :param replace: (string, optional):
            If current path is ``replace``, this method call :meth:`pop` before
            any action.
        :param anchor: (string, optional)
            Anchor to add.
        """
        # Environment
        session = self._request.session
        if 'breadcrumbs' not in session:
            session['breadcrumbs'] = [(_('Home'), 'home', {}, 1)]
        if not length:
            length = len(session['breadcrumbs'])

        # Replace
        if replace and self.current_path() == replace:
            self.pop()

        # Scan old breadcrumb trail to find the right position
        route_name = \
            self._request.matched_route and self._request.matched_route.name
        if route_name is None:
            return
        compare_name = route_name.replace('_root', '_browse')\
            .replace('_task', '').replace('_pack', '')
        crumbs = []
        for crumb in session['breadcrumbs']:
            crumb_name = crumb[1] and crumb[1].replace('_root', '_browse')\
                .replace('_task', '').replace('_pack', '')
            if len(crumbs) >= length - 1 or crumb_name == compare_name:
                break
            crumbs.append(crumb)

        # Add new breadcrumb
        params = self._request.matchdict
        if anchor is not None:
            params['_anchor'] = anchor
        crumbs.append((title, route_name, params, root_chunks))
        session['breadcrumbs'] = crumbs

    # -------------------------------------------------------------------------
    def pop(self):
        """Pop last breadcrumb."""
        session = self._request.session
        if 'breadcrumbs' in session and len(session['breadcrumbs']) > 1:
            session['breadcrumbs'] = session['breadcrumbs'][0:-1]


# =============================================================================
class Menu(object):
    """User menu management."""

    # -------------------------------------------------------------------------
    def __init__(self, request):
        """Constructor method."""
        self._request = request
        self._translate = get_localizer(request).translate

    # -------------------------------------------------------------------------
    def xhtml(self):
        """Output XHTML user menu."""
        if 'user_id' not in self._request.session:
            return ''
        if 'menu' in self._request.session:
            return self._make_xhtml()
        menu = []

        # Storages
        if has_permission(self._request, 'stg_user'):
            submenu = 'storage.index' in self._request.registry.settings \
                and [self._entry(_('Advanced search'), 'file_search'),
                     self._entry(_('All storages'), 'storage_index')] \
                or [self._entry(_('All storages'), 'storage_index')]
            self._storage_entries(self._request.session['user_id'], submenu)
            menu.append(self._entry(_('Storages'), None, submenu))

        # Projects
        if has_permission(self._request, 'prj_user'):
            submenu = [self._entry(_('All projects'), 'project_index')]
            self._project_entries(self._request.session['user_id'], submenu)
            menu.append(self._entry(_('Projects'), None, submenu))

        # Administration
        submenu = []
        if has_permission(self._request, 'admin'):
            submenu.append(self._entry(_('Site'), 'site_admin'))
        if has_permission(self._request, 'usr_editor'):
            submenu.append(self._entry(_('Users'), 'user_admin'))
        if has_permission(self._request, 'grp_editor'):
            submenu.append(self._entry(_('Groups'), 'group_admin'))
        if has_permission(self._request, 'stg_editor'):
            submenu.append(self._entry(_('Storages'), 'storage_admin'))
        if has_permission(self._request, 'idx_editor'):
            submenu.append(self._entry(_('Indexing'), 'indexer_admin'))
        if has_permission(self._request, 'prj_editor'):
            submenu.append(self._entry(_('Projects'), 'project_admin'))
        if submenu:
            menu.append(self._entry(_('Administration'), None, submenu))

        if not menu:
            return ''
        self._request.session['menu'] = tuple(menu)
        return self._make_xhtml()

    # -------------------------------------------------------------------------
    def _make_xhtml(self):
        """Return an <ul> structure with current highlighted current entry."""
        # Make XHTML
        menu = self._request.session['menu']
        xhtml = '<ul>%s</ul>' % self._make_xhtml_entries(menu, 0)

        # Highlight current entry
        # pylint: disable = locally-disabled, star-args
        if 'breadcrumbs' in self._request.session:
            for crumb in reversed(self._request.session['breadcrumbs'][1:]):
                if crumb[1] is None:
                    continue
                params = dict(
                    (k, crumb[2][k]) for k in crumb[2] if k != '_anchor')
                path = self._request.route_path(crumb[1], **params)
                path = '/'.join(path.split('/')[0:crumb[3] + 1])\
                       .replace('/edit/', '/view/')
                if 'href="%s"' % path in xhtml:
                    xhtml = xhtml.replace(
                        '<a class="slow" href="%s"' % path,
                        '<a class="slow current" href="%s"' % path)
                    break

        # Tag current project
        if 'project' in self._request.session:
            path = self._request.route_path(
                'project_dashboard',
                project_id=self._request.session['project']['project_id'],
                _query={'id': self._request.session['project']['project_id']})
            xhtml = xhtml.replace(
                '<li><a class="slow" href="%s"' % path,
                '<li class="active"><a class="slow" href="%s"' % path)

        return literal(xhtml)

    # -------------------------------------------------------------------------
    def _make_xhtml_entries(self, entries, depth):
        """Return <li> tags with entries.

        :param entries: (tuple)
            Tuple of entry tuples (See :meth:`_entry`)
        :param depth: (integer)
            Depth of entries in menu.
        """
        xhtml = ''
        for entry in entries:
            tag = (depth == 0 and '<strong>') \
                or (depth == 1 and entry[2] and '<em>') or ''
            xhtml += '<li>' \
                + (entry[1] and '<a class="slow" href="%s">' % entry[1] or '')\
                + tag + entry[0] + tag.replace('<', '</') \
                + (entry[1] and '</a>' or '')
            if entry[3]:
                xhtml += '<ul>%s</ul>' % self._make_xhtml_entries(
                    entry[3], depth + 1)
            xhtml += '</li>'
        return xhtml

    # -------------------------------------------------------------------------
    def _storage_entries(self, user_id, submenu):
        """Update menu entries for user storages shown in menu.

        :param user_id: (string)
            Current user ID.
        :param submenu: (list)
            Current submenu list.
        """
        # Look for user storages
        for storage in DBSession.query(Storage).join(StorageUser)\
                .filter(Storage.access != 'closed')\
                .filter(StorageUser.user_id == user_id)\
                .filter(StorageUser.in_menu == TRUE).order_by(Storage.label):
            submenu.append(self._entry(
                storage.label, 'storage_root', None, True,
                storage_id=storage.storage_id))

    # -------------------------------------------------------------------------
    def _project_entries(self, user_id, submenu):
        """Update menu entries for user projects shown in menu.

        :param user_id: (string)
            Current user ID.
        :param submenu: (list)
            Current submenu list.
        """
        groups = [k.group_id for k in DBSession.execute(
            select([GROUPS_USERS], GROUPS_USERS.c.user_id == user_id))]
        for project in DBSession.query(
                Project.project_id, Project.label, ProjectUser.perm,
                ProjectUser.entries).join(ProjectUser)\
                .filter(ProjectUser.user_id == user_id)\
                .filter(ProjectUser.in_menu == TRUE).order_by(Project.label):
            pid = project[0]
            subentries = [
                self._entry(_('Dashboard'), 'project_dashboard',
                            None, True, project_id=pid)]
            if project[3] in ('all', 'tasks'):
                subentries.append(self._entry(
                    _('Tasks'), 'task_index', None, True, project_id=pid))
            if project[3] in ('all', 'packs'):
                subentries.append(self._entry(
                    _('Packs'), 'pack_index', None, True, project_id=pid))
            subentries.append(self._entry(
                _('Last results'), 'build_results', None, True,
                project_id=pid))

            perm = has_permission(self._request, 'prj_editor') and 'leader' \
                or project[2]
            if perm != 'leader' and groups and 'leader' in \
                    [k[0] for k in DBSession.query(ProjectGroup.perm)
                     .filter_by(project_id=pid)
                     .filter(ProjectGroup.group_id.in_(groups))]:
                perm = 'leader'
            if perm == 'leader':
                subentries.append(self._entry(
                    _('Settings'), 'project_view', None, True, project_id=pid))

            submenu.append(self._entry(
                project[1], 'project_dashboard', tuple(subentries), True,
                project_id=pid, _query={'id': pid}))

    # -------------------------------------------------------------------------
    def _entry(self, label, route_name, subentries=None, is_minor=False,
               **kwargs):
        """A menu entry tuple.

        :param label: (string)
            Label of the entry.
        :param route_name: (string)
            Name of the route for the link.
        :param subentries: (list, optional)
            List of subentries.
        :param is_minor: (boolean, default=False)
            Indicate whether this entry is a minor one.
        :param kwargs: (dictionary)
            Keyworded arguments for :meth:`pyramid.request.Request.route_path`.
        :return: (tuple)
            A tuple such as
            ``(label, url, is_minor, (subentry, subentry...))``.
        """
        return (self._translate(label),
                route_name and self._request.route_path(route_name, **kwargs),
                is_minor, subentries and tuple(subentries))


# =============================================================================
class Paging(list):
    """Divide large lists of items into pages.

    This class uses two parameters in request: ``page_size`` and ``page``.

    It stores its information and filters definitions in ``session['paging']``.
    This structure looks like: ``session['paging'] = (default_page_size,
    {'projects': {'page_size': 20, 'page': 3, 'sort': 'name', 'f_id': 'smith',
    'f_group': 'managers',...}, ...})``
    """

    page_sizes = (' ', 5, 10, 20, 40, 80, 160, 320)

    # -------------------------------------------------------------------------
    def __init__(self, request, paging_id, collection, item_count=None,
                 default_sorting=None):
        """Constructor method.

        :param request: (:class:`pyramid.request.Request` instance)
            Current request.
        :param paging_id: (string)
            ID for the paging.
        :param collection: (list-like object)
            Collection object being paged through.
        :param item_count: (integer, optional)
            Number of items in the collection.
        :param default_sorting: (string, optional)
            Default sorting.
        """
        # Update paging session
        if 'paging' not in request.session \
           or paging_id not in request.session['paging'][1]:
            self.params(request, paging_id, default_sorting)
        params = request.session['paging'][1][paging_id]
        if 'page_size' in request.params \
           and request.params['page_size'].strip():
            params['page_size'] = max(1, int(request.params['page_size']))
        if request.params.get('page'):
            params['page'] = max(1, int(request.params['page']))

        # Initialize variables
        self.paging_id = paging_id
        full_list = collection
        if isinstance(collection, Query):
            full_list = _SQLAlchemyQuery(collection)
        self.item_count = item_count is not None and item_count \
            or len(full_list)
        self.page_count = ((self.item_count - 1) // params['page_size']) + 1
        if params['page'] > self.page_count:
            params['page'] = self.page_count
        self.page = max(1, params['page'])
        self.first_item = None
        self.items = []
        self._request = request

        # Compute the item list
        if self.item_count > 0:
            self.first_item = (self.page - 1) * params['page_size'] + 1
            last_item = min(
                self.first_item + params['page_size'] - 1, self.item_count)
            try:
                self.items = list(full_list[self.first_item - 1:last_item])
            except TypeError:
                raise TypeError("You can't use type %s!" % type(full_list))

        list.__init__(self, self.items)

    # -------------------------------------------------------------------------
    @classmethod
    def params(cls, request, paging_id, default_sorting):
        """Return current paging parameters: filter criteria and sorting.

        :param paging_id: (string)
            Paging ID.
        :param default_sorting: (string)
            Default sorting.
        :return: (dictionary)
            The paging dictionary. See :class:`~.widget.Paging` class.
        """
        if 'paging' not in request.session:
            request.session['paging'] = (PAGE_SIZE, {})
        if paging_id not in request.session['paging'][1]:
            request.session['paging'][1][paging_id] = {
                'page_size': request.session['paging'][0],
                'page': 1, 'sort': default_sorting}
        params = request.session['paging'][1][paging_id]
        if params['sort'] is None:
            params['sort'] = default_sorting

        if len(request.POST):
            request.session['paging'][1][paging_id] = {
                'page_size': params['page_size'], 'page': params['page'],
                'sort': params['sort']}
            params = request.session['paging'][1][paging_id]

        for key in request.params:
            if (key[0:2] == 'f_' or key == 'sort') and request.params[key]:
                params[key] = request.params[key]

        return params

    # -------------------------------------------------------------------------
    def pager(self, pager_format='~3~', symbol_first='&lt;&lt;',
              symbol_last='&gt;&gt;', symbol_previous='&lt;',
              symbol_next='&gt;'):
        """Return string with links to other pages (e.g. '1 .. 5 6 7 [8] 9 10
        11 .. 50').

        :param pager_format: (string, default='~3~')
            Format string that defines how the pager is rendered.
        :param symbol_first: (string, default='&lt;&lt;')
            String to be displayed as the text for the $link_first link above.
        :param symbol_last: (string, default='&gt;&gt;')
            String to be displayed as the text for the $link_last link above.
        :param symbol_previous: (string, default='&lt;')
            String to be displayed as the text for the $link_previous link
            above.
        :param symbol_next: (string, default='&gt;')
            String to be displayed as the text for the $link_next link above.

        Format string that defines how the pager is rendered. The string
        can contain the following $-tokens that are substituted by the
        string.Template module:

        - $first_page: number of first reachable page
        - $last_page: number of last reachable page
        - $page: number of currently selected page
        - $page_count: number of reachable pages
        - $items_per_page: maximal number of items per page
        - $first_item: index of first item on the current page
        - $last_item: index of last item on the current page
        - $item_count: total number of items
        - $link_first: link to first page (unless this is first page)
        - $link_last: link to last page (unless this is last page)
        - $link_previous: link to previous page (unless this is first page)
        - $link_next: link to next page (unless this is last page)

        To render a range of pages the token '~3~' can be used. The number sets
        the radius of pages around the current page.
        Example for a range with radius 3: '1 .. 5 6 7 [8] 9 10 11 .. 50'
        """
        # pylint: disable = locally-disabled, R0913
        if self.page_count < 2:
            return ''

        # Replace ~...~ in token format by range of pages
        result = re.sub(r'~(\d+)~', self._range, pager_format)

        # Interpolate '$' variables
        items_per_page = self._request.params.get('page_size') \
            and max(1, int(self._request.params['page_size'])) \
            or self._request.session['paging'][1][self.paging_id]['page_size']
        query_string = self._request.GET.copy()
        query_string.update({'paging_id': self.paging_id})

        return literal(Template(result).safe_substitute({
            'first_page': 1,
            'last_page': self.page_count,
            'page': self.page,
            'page_count': self.page_count,
            'items_per_page': items_per_page,
            'first_item': self.first_item,
            'last_item': min(
                self.first_item + items_per_page - 1, self.item_count),
            'item_count': self.item_count,
            'link_first': self.page > 1 and self._link(
                query_string, 1, symbol_first) or '',
            'link_last': self.page < self.page_count and self._link(
                query_string, self.page_count, symbol_last) or '',
            'link_previous': self.page > 1 and self._link(
                query_string, self.page - 1, symbol_previous) or '',
            'link_next': self.page < self.page_count and self._link(
                query_string, self.page + 1, symbol_next) or ''
        }))

    # -------------------------------------------------------------------------
    def pager_top(self, icon_name=None, label=None):
        """Output a string with links to first, previous, next and last pages.

        :param icon_name: (string, optional)
            Name of the icon representing the items.
        :param label: (string, optional)
            Label representing the items.
        :return: (string)
        """
        icon = ''
        if icon_name is not None and label is not None:
            icon = literal(
                u'<img src="/Static/Images/{0}.png" alt="{1}"'
                ' title="{1}"/>&nbsp;'.format(icon_name, label))
        img = '<img src="/Static/Images/go_%s.png" alt="%s"/>'
        return icon + self.pager(
            '$link_first $link_previous '
            '<span>$first_item &ndash; $last_item</span> / $item_count '
            '$link_next $link_last',
            symbol_first=literal(img % ('first', 'First')),
            symbol_previous=literal(img % ('previous', 'Previous')),
            symbol_next=literal(img % ('next', 'Next')),
            symbol_last=literal(img % ('last', 'Last'))) or literal('&nbsp;')

    # -------------------------------------------------------------------------
    def pager_bottom(self, icon_name=None, label=None):
        """Output a string with links to some previous and next pages.

        :param icon_name: (string, optional)
            URL of the icon representing the items.
        :param label: (string, optional)
            Label representing the items.
        :return: (string)
        """
        icon = ''
        if icon_name is not None and label is not None:
            icon = literal(
                u'<img src="/Static/Images/{0}.png" alt="{1}"'
                ' title="{1}"/> &nbsp;'.format(icon_name, label))
        return (icon + self.pager()) or literal('&nbsp;')

    # -------------------------------------------------------------------------
    def sortable_column(self, label, sort):
        """Output a header of column with `sort up` and `sort down` buttons.

        See :func:`~.lib.utils.sortable_column`.

        :param label: (string)
             Label of column.
        :param sort: (string)
             Sort criteria.
        :return: (literal HTML string)
        """
        return sortable_column(
            self._request, label, sort,
            self._request.session['paging'][1][self.paging_id]['sort'],
            self.paging_id)

    # -------------------------------------------------------------------------
    @classmethod
    def pipe(cls):
        """Output a pipe image."""
        return literal(
            '<img src="/Static/Images/action_pipe.png" alt="Pipe"/>')

    # -------------------------------------------------------------------------
    def _range(self, regexp_match):
        """Return range of linked pages (e.g. '1 2 [3] 4 5 6 7 8').

        :param regexp_match: (:class:`re.Match` instance)
            A regular expressions match object containing the radius of linked
            pages around the current page in regexp_match.group(1) as a string.
        :return: (string)
        """
        query_string = self._request.GET.copy()
        query_string.update({'paging_id': self.paging_id})
        radius = int(regexp_match.group(1))
        leftmost_page = max(1, self.page - radius)
        rightmost_page = min(self.page + radius, self.page_count)
        items = []

        if self.page != 1 and 1 < leftmost_page:
            items.append(self._link(query_string, 1, '1'))
        if leftmost_page > 2:
            items.append('..')
        for page in range(leftmost_page, rightmost_page + 1):
            if page == self.page:
                items.append('<span>%d</span>' % page)
            else:
                items.append(self._link(query_string, page, str(page)))
        if rightmost_page < self.page_count - 1:
            items.append('..')
        if self.page != self.page_count and rightmost_page < self.page_count:
            items.append(self._link(
                query_string, self.page_count, str(self.page_count)))

        return ' '.join(items)

    # -------------------------------------------------------------------------
    def _link(self, query_string, page_number, label):
        """Create an A-HREF tag that points to another page.

        :param query_string: (dictionary)
            The current query string in a dictionary.
        :param page_number: (integer)
            Number of the page that the link points to
        :param label: (string)
            Text to be printed in the A-HREF tag
         """
        query_string.update({'page': page_number})
        return tags.link_to(
            label,
            '%s?%s' % (self._request.path, urlencode(query_string, True)))


# =============================================================================
class TabSet(object):
    """A class to manages tabs."""

    # -------------------------------------------------------------------------
    def __init__(self, request, labels):
        """Constructor method."""
        self._request = request
        self.labels = labels

    # -------------------------------------------------------------------------
    def toc(self, tab_id):
        """Output a table of content of the ``TabSet`` in an ``<ul>``
        structure.

        :param tab_id: (string)
            Tab set ID.
        :return: (string)
            ``<ul>`` structure.
        """
        translate = get_localizer(self._request).translate
        xml = '<ul id="%s" class="tabs">\n' % tab_id
        for index, label in enumerate(self.labels):
            xml += '  <li><a class="tab" id="tab%d" href="#tabContent%d">' \
                   '<span>%s</span></a></li>\n' \
                   % (index, index, translate(label))
        xml += '</ul>\n'
        return literal(xml)

    # -------------------------------------------------------------------------
    def tab_begin(self, index, access_key=None):
        """Open a tab zone.

        :param index: (integer)
            Tab index.
        :param access_key: (string, optional)
            Access key for tab.
        :return: (string)
            Opening ``fieldset`` structure with legend.
        """
        return literal(
            '<fieldset class="tabContent" id="tabContent%d">\n'
            '  <legend%s><span>%s</span></legend>\n'
            % (index, access_key and ' accesskey="%s"' % access_key or '',
               get_localizer(self._request).translate(self.labels[index])))

    # -------------------------------------------------------------------------
    @classmethod
    def tab_end(cls):
        """Close a tab zone."""
        return literal('</fieldset>')


# =============================================================================
class _SQLAlchemyQuery(object):
    """Iterable that allows to get slices from an SQLAlchemy Query object."""
    # pylint: disable = locally-disabled, R0903

    # -------------------------------------------------------------------------
    def __init__(self, query):
        """Contructor method."""
        self.query = query

    # -------------------------------------------------------------------------
    def __getitem__(self, records):
        """Implement evaluation of self[key]."""
        if not isinstance(records, slice):
            raise Exception('__getitem__ without slicing not supported')
        return self.query[records]

    # -------------------------------------------------------------------------
    def __len__(self):
        """Implement the built-in function len()."""
        return self.query.count()
