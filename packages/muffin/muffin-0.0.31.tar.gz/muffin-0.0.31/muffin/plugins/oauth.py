import asyncio
from muffin.plugins import BasePlugin
from muffin.utils import to_coroutine
from oauthlib import oauth2
import functools


class OAuthException(Exception):
        pass


class OAuth2Plugin(BasePlugin):

    """ Support OAuth. """

    name = 'oauth2'
    defaults = {
        'clients': {}
    }

    def setup(self, app):
        """ Initialize the application. """
        super().setup(app)
        self.clients = {}
        for name in self.options['clients']:
            self.clients[name] = oauth2.Client(self.options['clients'][name]['id'])

    def handle(self, name):
        try:
            client = self.clients[name]
        except KeyError:
            raise OAuthException('Unconfigured OAuth2 client: %s' % name)

        def decorator(view):
            view = to_coroutine(view)

            @asyncio.coroutine
            @functools.wraps(view)
            def wrapper(request):
                return (yield from view(request))

            return wrapper

        return decorator
