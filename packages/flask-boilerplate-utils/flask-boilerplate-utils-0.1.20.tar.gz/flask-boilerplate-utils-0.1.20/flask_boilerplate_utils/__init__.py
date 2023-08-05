from flask import Blueprint
from .jinja_globals import render_field, csrf_setup
from .filters import (
    timesince,
    local_date,
    percent_escape,
    local_date_time,
    get_autoincluded_assets
)
from flask.ext.babel import Babel


class Boilerplate(object):
    """
    Configure the App with the standard boilerplate
    configuration.

    :param app: the Flask Applciation
    :param csrf_enabled: A boolean determining whether or not
                         flask_wtf CSRF protection should
                         be enabled.
    :param use_sentry: A boolean determining whether or not
                       Sentry should be used within the 
                       production environment.
    """

    def __init__(self, app=None, **kwargs):
        self.app = app

        if app is not None:
            self._state = self.init_app(app, **kwargs)

    def init_app(self, app, csrf_enabled=True,
        use_sentry=True, with_html_assets=True,
        with_redis_sessions=False,
        redis_db_number=1,
        behind_reverse_proxy=False):
        bp = Blueprint(
            'boilerplate',
            __name__,
            template_folder='templates',
            url_prefix='/bp',
        )

        app.register_blueprint(bp)
        app.jinja_env.globals['csrf_setup'] = csrf_setup
        app.jinja_env.globals['render_field'] = render_field
        if with_html_assets:
            app.jinja_env.globals['html_assets'] = get_autoincluded_assets(app)()
        app.jinja_env.filters['local_date'] = local_date
        app.jinja_env.filters['local_date_time'] = local_date_time
        app.jinja_env.filters['percent_escape'] = percent_escape
        app.jinja_env.filters['time_since'] = timesince

        app.babel = Babel(app)

        if csrf_enabled:
            from flask_wtf.csrf import CsrfProtect
            app.csrf = CsrfProtect(app)

        if behind_reverse_proxy:
            from .ReverseProxied import ReverseProxied
            app.wsgi_app = ReverseProxied(app.wsgi_app)

        # Setup App Debug via Sentry (When in production)
        if use_sentry and not app.debug:
            from raven.contrib.flask import Sentry
            app.sentry = Sentry(app)

        if with_redis_sessions or app.config.get('USE_REDIS_SESSIONS', False):
            from .RedisSessionInterface import RedisSessionInterface
            from redis import Redis
            redis = Redis(db=redis_db_number)
            app.session_interface = RedisSessionInterface(redis=redis)



