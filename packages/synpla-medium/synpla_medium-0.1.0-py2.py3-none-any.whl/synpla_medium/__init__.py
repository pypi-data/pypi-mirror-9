__version__ = '0.1.0'


from flask import Blueprint


class SynplaMedium(object):
    """Medium Editor JS functionality for SynPla."""

    def __init__(self, app=None):
        self.app = app

        if self.app:
            self.init_app(self.app)

    def init_app(self, app):
        """ Configures synpla-medium."""

        blueprint = Blueprint(
            'medium',
            __name__,
            template_folder='templates',
            static_folder='static',
            static_url_path=app.static_url_path + '/medium')

        app.register_blueprint(blueprint)
