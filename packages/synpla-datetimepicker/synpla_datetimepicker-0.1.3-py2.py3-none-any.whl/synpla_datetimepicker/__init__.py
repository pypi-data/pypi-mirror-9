__version__ = '0.1.3'


from flask import Blueprint


class SynplaDatetimepicker(object):
    """Date / time picker JS functionality for SynPla."""

    def __init__(self, app=None):
        self.app = app

        if self.app:
            self.init_app(self.app)

    def init_app(self, app):
        """ Configures synpla-datetimepicker."""

        blueprint = Blueprint(
            'datetimepicker',
            __name__,
            template_folder='templates',
            static_folder='static',
            static_url_path=app.static_url_path + '/datetimepicker')

        app.register_blueprint(blueprint)
