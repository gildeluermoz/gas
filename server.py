
"""
    Serveur de l'application GAS
"""

import json
import os
from flask import Flask, redirect, url_for, request, session, render_template
from flask_bootstrap import Bootstrap
import flask_excel as excel
from app.env import db
from config import config


class ReverseProxied(object):

    def __init__(self, app, script_name=None, scheme=None, server=None):
        self.app = app
        self.script_name = script_name
        self.scheme = scheme
        self.server = server

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '') or self.script_name
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]
        scheme = environ.get('HTTP_X_SCHEME', '') or self.scheme
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        server = environ.get('HTTP_X_FORWARDED_SERVER', '') or self.server
        if server:
            environ['HTTP_HOST'] = server
        return self.app(environ, start_response)


app = Flask(
    __name__,
    template_folder="app/templates",
    static_folder='app/static'
)

Bootstrap(app)

app.wsgi_app = ReverseProxied(app.wsgi_app, script_name=config.URL_APPLICATION)

app.config.from_pyfile('config/config.py')
app.secret_key = config.SECRET_KEY

db.init_app(app)
app.config['DB'] = db

excel.init_excel(app)

with app.app_context():
    app.jinja_env.globals['url_application'] = app.config["URL_APPLICATION"]

    if config.ACTIVATE_APP:
        @app.route('/')
        def index():
            ''' Route par défaut de l'application '''
            if "current_user" in session.keys():
                if session["current_user"]:
                    if session["current_user"]['id_profil'] > 2:
                        return redirect(url_for('delivery.deliveries'))
                    else:
                        return redirect(url_for('user.users'))
                else:
                    return render_template('login.html', id_app=0)
            else:
                return render_template('login.html', id_app=0)

        @app.route('/constants.js')
        def constants_js():
            ''' Route des constantes javascript '''
            return render_template('constants.js')

        @app.after_request
        def after_login_method(response):
            '''
                Fonction s'exécutant après chaque requete
                permet de gérer l'authentification
            '''
            if not request.cookies.get('token'):
                session["current_user"] = None

            if request.endpoint == 'auth.login' and response.status_code == 200: # noqa
                current_user = json.loads(response.get_data().decode('utf-8'))
                session["current_user"] = current_user["user"]
            return response

        from app.pypnusershub import route
        app.register_blueprint(route.route, url_prefix='/auth')

        from app.t_users import route
        app.register_blueprint(route.route, url_prefix='/')

        from app.t_groups import route
        app.register_blueprint(route.route, url_prefix='/')

        from app.t_deliveries import route
        app.register_blueprint(route.route, url_prefix='/')

        from app.t_products import route
        app.register_blueprint(route.route, url_prefix='/')

        from app.t_profils import route
        app.register_blueprint(route.route, url_prefix='/')

        from app.t_orders import route
        app.register_blueprint(route.route, url_prefix='/')

        from app.login import route
        app.register_blueprint(route.route, url_prefix='/login')

if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=config.DEBUG, port=config.PORT)
