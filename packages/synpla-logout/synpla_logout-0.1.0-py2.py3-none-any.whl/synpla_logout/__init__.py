__version__ = '0.1.0'


from flask import Blueprint


class SynplaLogout(object):
    """Logout JS functionality for SynPla."""

    def __init__(self, app=None):
        self.app = app

        if self.app:
            self.init_app(self.app)

    def init_app(self, app):
        """ Configures synpla-logout."""

        blueprint = Blueprint(
            'logout',
            __name__,
            static_folder='static',
            static_url_path=app.static_url_path + '/logout')

        app.register_blueprint(blueprint)
