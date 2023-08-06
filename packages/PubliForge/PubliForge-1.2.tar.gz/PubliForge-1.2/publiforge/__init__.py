# $Id: __init__.py 25ef6529a14f 2014/06/29 10:37:43 Patrick $
"""The :func:`.main` function is called when the ``pserve`` command is invoked
against this application.
"""

from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from .initialize import Initialize, perm_group_finder, RootFactory


__credits__ = '(c) Prismallia http://www.prismallia.fr, 2014'


# =============================================================================
def main(global_config, **settings):
    """This is the main function. It returns a Pyramid WSGI application.

    :param global_config: (dictionary)
        Default section of INI file.
    :param settings: (dictionary)
        Application settings of [app:publiforge] section of INI file.
    :return: (object)
        WSGI application.

    It creates an instance of :class:`~.initialize.Initialize` class and call
    its :meth:`~.initialize.Initialize.all` method to initialize the
    application.
    """
    authentication_policy = AuthTktAuthenticationPolicy(
        secret=settings.get('encryption', '-'), hashalg='sha512',
        cookie_name=settings.get('auth.cookie', 'PF_AUTH'),
        callback=perm_group_finder)
    authorization_policy = ACLAuthorizationPolicy()
    config = Configurator(settings=settings,
                          root_factory=RootFactory,
                          authentication_policy=authentication_policy,
                          authorization_policy=authorization_policy)
    config.include('pyramid_chameleon')

    Initialize(global_config, config).all()

    return config.make_wsgi_app()
