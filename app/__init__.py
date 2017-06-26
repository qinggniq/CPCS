from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .personaluser import person as personaluser_blueprint
    app.register_blueprint(personaluser_blueprint, url_prefix='/person')

    from .collection import collection as collection_blueprint
    app.register_blueprint(collection_blueprint, url_prefix='/collection')

    from .manager import  manager as manager_blueprint
    app.register_blueprint(manager_blueprint, url_prefix='/manager')

    from .admin import  admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')


    return app
