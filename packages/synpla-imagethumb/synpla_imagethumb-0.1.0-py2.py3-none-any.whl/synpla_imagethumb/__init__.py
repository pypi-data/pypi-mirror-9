__version__ = '0.1.0'


from flask import Blueprint


class SynplaImagethumb(object):
    """An 'imagethumb' template macro for SynPla."""

    def __init__(self, app=None):
        self.app = app

        if self.app:
            self.init_app(self.app)

    def init_app(self, app):
        """ Configures synpla-imagethumb."""

        blueprint = Blueprint(
            'imagethumb',
            __name__,
            template_folder='templates')

        app.register_blueprint(blueprint)
