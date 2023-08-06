__version__ = '0.1.1'


from flask import Blueprint


class SynplaWeight(object):
    """Weight JS functionality for SynPla."""

    def __init__(self, app=None):
        self.app = app

        if self.app:
            self.init_app(self.app)

    def init_app(self, app):
        """ Configures synpla-weight."""

        blueprint = Blueprint(
            'weight',
            __name__,
            template_folder='templates',
            static_folder='static',
            static_url_path=app.static_url_path + '/weight')

        app.register_blueprint(blueprint)
