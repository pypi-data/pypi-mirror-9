import asyncio
from . import BasePlugin
from oauthlib import oauth2


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
        from requests import Session
        import ipdb; ipdb.set_trace()  # XXX BREAKPOINT

    def handle(self, view):
        if not asyncio.iscoroutinefunction(view):
            view = asyncio.coroutine(view)

        @asyncio.coroutine
        def wrapper(request):
            return (yield from view(request))

        return wrapper
