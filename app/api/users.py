from flask import jsonify, request, url_for
from app import db
from app.models import User
from .errors import bad_request
from . import bp


# Get user's data
@bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
	return jsonify(User.query.get_or_404(id).to_dict())

# Get all users data.
@bp.route('/users', methods=['GET'])
def get_users():
	page = request.args.get('page', 1, type=int)
	per_page = min(request.args.get('per_page', 10, type=int), 100)
	data = User.to_collection_dict(query=User.query, page=page,
			per_page=per_page, endpoint='api.get_users')
	return jsonify(data)


@bp.route('/users/<int:id>/cars', methods=['GET'])
def get_user_cars(id):
	user = User.query.get_or_404(id)
	page = request.args.get('page', 1, type=int)
	per_page = min(request.args.get('per_page', 10, type=int), 100)
	data = User.to_collection_dict(query=user.cars, page=page, per_page=per_page,
								   endpoint='api.get_user_cars', id=id)
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
def update_user(id):
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