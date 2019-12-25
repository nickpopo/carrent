import os

from flask import Flask, request
from config import Config

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap


db = SQLAlchemy()
migrate = Migrate()

login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'

mail = Mail()

bootstrap = Bootstrap()


# Application Factory.
def create_app(config_class=Config):

	# App configs.
	app = Flask(__name__)
	app.config.from_object(config_class)

	# Initialize extensions.
	db.init_app(app)
	migrate.init_app(app, db)
	login.init_app(app)
	mail.init_app(app)
	bootstrap.init_app(app)

	# Blueprints registration.
	from app.auth import bp as auth_bp
	app.register_blueprint(auth_bp, url_prefix='/auth')

	from app.admin import bp as admin_bp
	app.register_blueprint(admin_bp, url_prefix='/admin')

	from app.errors import bp as errors_bp
	app.register_blueprint(errors_bp)

	from app.main import bp as main_bp
	app.register_blueprint(main_bp)

	return app