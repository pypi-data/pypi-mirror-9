# $Id: debug.py e97a03429719 2014/09/19 12:26:17 Patrick $
"""Debug or testing functions and classes."""
import logging
import cgi
import re
from subprocess import PIPE, STDOUT, Popen

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import NO_PERMISSION_REQUIRED, remember

from .viewutils import connect_user
from ..models import close_dbsession


LOG = logging.getLogger(__name__)


# =============================================================================
def includeme(config):
    """Include HTML validator."""
    config.add_tween('publiforge.lib.debug.htmlvalidator_tween_factory')


# =============================================================================
def htmlvalidator_tween_factory(handler, registry):
    """HTML validator tween factory.

    :param handler: (:class:`pyramid.request.Request` instance)
    :param registry: (:class:`pyramid.registry.Registry` instance)
    :return: (:class:`pyramid.response.Response` instance)
    """
    # pylint: disable = locally-disabled, W0613
    def htmlvalidator_tween(request):
        """HTML validator tween."""
        # Is a OK HTML?
        response = handler(request)
        if response.status_int != 200 or 'html' not in response.content_type \
           or request.is_xhr:
            return response

        # Validate
        cmd = 'xml' in response.content_type and ['validate', '--xml'] \
              or ['validate']
        html = response.body\
            .replace(
                '<!DOCTYPE html>',
                '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"'
                ' "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">')\
            .replace('<meta charset="utf-8"/>', '')\
            .replace('<audio ', '<!--<audio ')\
            .replace('</audio>', '</audio>-->')\
            .replace('<video ', '<!--<video ')\
            .replace('</video>', '</video>-->')
        html = re.sub(' (lang|data-[a-z_-]+|draggable)="[^"]+"', '', html)
        error = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT)\
            .communicate(html)[0]

        # Error?
        if error:
            error = error.decode('utf8')
            LOG.error('%s: %s', request.current_route_url(), error.strip())
            error = '<pre style="background-color: #ffffdd; color: #993333;'\
                    ' border: 1px solid #993333; padding: 1ex;">%s</pre>\n' \
                    % cgi.escape(error)
            match = re.search(r'</body>', response.text, re.I)
            if match:
                response.text = u'%s%s%s' % (
                    response.text[:match.start()], error,
                    response.text[match.start():])
            else:
                response.text += error
            response.content_length = str(len(response.body))

        return response

    return htmlvalidator_tween


# =============================================================================
@view_config(route_name='login_test', permission=NO_PERMISSION_REQUIRED)
def login_test(request):
    """Quick log in for test only."""
    user_login = request.params.get('login')
    if 'paste.testing' not in request.environ or user_login is None:
        close_dbsession(request)
        return HTTPFound(location=request.route_path('login'))
    # pylint: disable = locally-disabled, E1103
    user = connect_user(request, user_login)
    user.setup_environment(request)
    close_dbsession(request)
    return HTTPFound('/robots.txt', headers=remember(request, user.login))
