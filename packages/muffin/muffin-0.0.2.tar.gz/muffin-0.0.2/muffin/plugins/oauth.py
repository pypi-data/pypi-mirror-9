import oauth2
import asyncio


class OAuthPlugin(object):

    """ Support OAuth. """

    defaults = {}
    name = 'oauth'

    def __init__(self):
        self.app = None
        self.options = None

    def setup(self, app):
        """ Initialize the application. """
        self.app = app
        self.app.oauth = self
        app.config.setdefault('OAUTH', self.defaults)
        self.options = app.config['OAUTH']

    def handle(self, view):
        if not asyncio.iscoroutinefunction(view):
            view = asyncio.coroutine(view)

        @asyncio.coroutine
        def wrapper(request):
            return (yield from view(request))

        return wrapper
