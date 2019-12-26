from flask import render_template, request
from app import db
from . import bp
from app.api.errors import error_response as api_error_response
from .helpers import wants_json_response


@bp.app_errorhandler(404)
def not_found_error(error):
	if wants_json_response():
		return api_error_response(404)
	return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
	db.session.rollback()
	if wants_json_response():
		return api_error_response(500)
	return render_template('errors/500.html'), 500