from . import BasePlugin
import flask as f
import flask_admin as fa


class AdminPlugin(BasePlugin):

    """ Implement admin interface. """

    name = 'admin'
    defaults = {
        'route': '/admin',
    }

    def setup(self, app):
        super().setup(app)

        fapp = f.Flask(app.name)
        self.admin = fa.Admin(fapp, url=self.options['route'])
