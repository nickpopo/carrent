from flask import jsonify, request, url_for, g, abort
from app import db
from app.models import User
from .auth import token_auth
from .decorators import admin_required
from .errors import bad_request
from . import bp


# Get user's data
@bp.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
	if g.current_user.id != id and not g.current_user.is_administrator():
		abort(403)
	return jsonify(User.query.get_or_404(id).to_dict())

# Get all users data.
@bp.route('/users', methods=['GET'])
@token_auth.login_required
@admin_required
def get_users():
	page = request.args.get('page', 1, type=int)
	per_page = min(request.args.get('per_page', 10, type=int), 100)
	data = User.to_collection_dict(query=User.query, page=page,
			per_page=per_page, endpoint='api.get_users')
	return jsonify(data)


@bp.route('/users/<int:id>/cars', methods=['GET'])
@token_auth.login_required
def get_user_cars(id):
	if g.current_user.id != id and not g.current_user.is_administrator():
		abort(403)
	user = User.query.get_or_404(id)
	page = request.args.get('page', 1, type=int)
	per_page = min(request.args.get('per_page', 10, type=int), 100)
	data = User.to_collection_dict(query=user.cars, page=page, per_page=per_page,
								   endpoint='api.get_user_cars', id=id, lang_code=g.current_user.language.code)
	return jsonify(data)


@bp.route('/users', methods=['POST'])
def create_user():
	data = request.get_json() or {}
	required = ('username', 'email', 'password', 'language_code')
	for field in required:
		if field not in data:
			return bad_request('must include username, email, language and password fields')
	if User.query.filter_by(username=data['username']).first():
		return bad_request('please use a different username.')
	if User.query.filter_by(email=data['email']).first():
		return bad_request('please use a different email address')
	user = User()
	user.from_dict(data, new_user=True)
	db.session.add(user)
	db.session.commit()
	response = jsonify(user.to_dict())
	response.status_code = 201
	response.headers['Location'] = url_for('api.get_user', id=user.id)
	return response


@bp.route('/users/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_user(id):
	# Prevent modify user's profile by another user.
	if g.current_user.id != id and not g.current_user.is_administrator():
		abort(403)
	user = User.query.get_or_404(id)
	data = request.get_json() or {}
	if 'username' in data and data['username'] != user.username and \
			User.query.filter_by(username=data['username']).first():
		return bad_request('please use a different username')
	if 'email' in data and data['email'] != user.email and \
			User.query.filter_by(email=data['email']).first():
		return bad_request('please use a different email address')
	user.from_dict(data, new_user=False)
	db.session.commit()
	return jsonify(user.to_dict())