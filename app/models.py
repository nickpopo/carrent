import os
import base64
from hashlib import md5
from datetime import datetime, timedelta
from time import time
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, url_for
from app import db, login
from flask_login import UserMixin, AnonymousUserMixin


### Mixins classes ###
class FormChoicesMixin(object):
	
	@classmethod
	def choices(cls):
		choices = []
		for obj in cls.query.all():
			choices.append((obj.id, obj.get_name()))
		return choices

class PaginatedAPIMixin(object):
	@staticmethod
	def to_collection_dict(query, page, per_page, endpoint, **kwargs):
		resources = query.paginate(page, per_page, False)
		data = {
			'meta': {
				'page': page,
				'per_page': per_page,
				'total_pages': resources.pages,
				'total_items': resources.total
			},
			'_links': {
				'self': url_for(endpoint, page=page, per_page=per_page,
								**kwargs),
				'next': url_for(endpoint, page=page + 1, per_page=per_page,
								**kwargs) if resources.has_next else None,
				'prev': url_for(endpoint, page=page - 1, per_page=per_page,
								**kwargs) if resources.has_prev else None
			}
		}
		if kwargs.get('lang_code'):
			data['items'] = [item.to_dict(lang_code=kwargs['lang_code']) for item in resources.items]
		elif kwargs.get('include_email'):
			data['items'] = [item.to_dict(include_email=kwargs['include_email']) for item in resources.items]
		else:
			data['items'] = [item.to_dict() for item in resources.items]
		return data

### End Mixins classes ###


class Permission:
	USER = 1
	ADMIN = 2

class Role(FormChoicesMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	default = db.Column(db.Boolean, default=False, index=True)
	permissions = db.Column(db.Integer)
	users = db.relationship('User', backref='role', lazy='dynamic')

	def __repr__(self):
		return '<Role {}>'.format(self.name)

	def __init__(self, **kwargs):
		super(Role, self).__init__(**kwargs)
		if self.permissions is None:
			self.permissions = 0

	@staticmethod
	def insert_roles():
		roles = {
			'User': [Permission.USER],
			'Administrator': [Permission.USER, Permission.ADMIN]
		}
		default_role = 'User'
		for r in roles:
			role = Role.query.filter_by(name=r).first()
			if role is None:
				role = Role(name=r)
			role.reset_permissions()
			for perm in roles[r]:
				role.add_permission(perm)
			role.default = (role.name == default_role)
			db.session.add(role)
		db.session.commit()

	def add_permission(self, perm):
		if not self.has_permission(perm):
			self.permissions += perm

	def remove_permission(self, perm):
		if self.has_permission(perm):
			self.permissions -= perm

	def reset_permissions(self):
		self.permissions = 0

	def has_permission(self, perm):
		return self.permissions & perm == perm

	def get_name(self):
		return self.name


########################
###### USER MODEL ######
########################
usercar_table = db.Table('usercar', db.Model.metadata,
	db.Column('user_id', db.Integer, db.ForeignKey('user.id'),
			  primary_key=True),
	db.Column('car_id', db.Integer, db.ForeignKey('car.id'),
			  primary_key=True)
	)

class User(PaginatedAPIMixin, UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	language_id = db.Column(db.Integer, db.ForeignKey('language.id'))
	language = db.relationship('Language', back_populates='users')
	role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
	cars = db.relationship('Car', secondary=usercar_table,
				back_populates='users', lazy='dynamic')
	timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
	token = db.Column(db.String(32), index=True, unique=True)
	token_expiration = db.Column(db.DateTime)

	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		if self.role is None:
			if self.email == current_app.config['ADMINS'][0]:
				self.role = Role.query.filter_by(name='Administrator').first()
			if self.role is None:
				self.role = Role.query.filter_by(default=True).first()

	def __repr__(self):
		return '<User {}>'.format(self.username)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def get_reset_password_token(self, expires_in=600):
		return jwt.encode(
			{'reset_password': self.id, 'exp': time() + expires_in},
			current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

	@staticmethod
	def verify_reset_password_token(token):
		try:
			id = jwt.decode(token, current_app.config['SECRET_KEY'],
							algorithms=['HS256'])['reset_password']
		except:
			return
		return User.query.get(id)

	def can(self, perm):
		return self.role is not None and self.role.has_permission(perm)

	def is_administrator(self):
		return self.can(Permission.ADMIN)

	# Related to api functional.
	def get_token(self, expires_in=3600):
		now = datetime.utcnow()
		if self.token and self.token_expiration > now + timedelta(seconds=60):
			return self.token
		self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
		self.token_expiration = now + timedelta(seconds=expires_in)
		db.session.add(self)
		return self.token

	def revoke_token(self):
		self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

	@staticmethod
	def check_token(token):
		user = User.query.filter_by(token=token).first()
		if user is None or user.token_expiration < datetime.utcnow():
			return None
		return user

	def to_dict(self, include_email=False):
		data = {
			'id': self.id,
			'username': self.username,
			'language_code': self.language.code,
			'car_count': self.cars.count(),
			'_links': {
				'self': url_for('api.get_user', id=self.id),
				'cars': url_for('api.get_user_cars', id=self.id)
			}
		}
		if include_email:
			data['email'] = self.email
		return data

	def from_dict(self, data, new_user=False):
		for field in ['username', 'email', 'language_code']:
			if field in data:
				if field == 'language_code':
					language = Language.query.filter_by(code=data[field]).first()
					setattr(self, 'language', language)
				setattr(self, field, data[field])
		if new_user and 'password' in data:
			self.set_password(data['password'])


class AnonymousUser(AnonymousUserMixin):
	def can(self, permissions):
		return False

	def is_administrator(self):
		return False

login.anonymous_user = AnonymousUser

@login.user_loader
def load_user(id):
	return User.query.get(int(id))


class Language(db.Model, FormChoicesMixin):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	code = db.Column(db.String(5), unique=True)
	users = db.relationship('User', back_populates='language')
	cars = db.relationship('CarLanguage', back_populates='language')

	def __repr__(self):
		return '<Language {}>'.format(self.code)

	@staticmethod
	def insert_values():
		values = [('English', 'en'),
				  ('Русский', 'ru')]
		for name, code in values:
			exist = Language.query.filter_by(code=code).first()
			if exist:
				continue
			new_lang = Language(name=name, code=code)
			db.session.add(new_lang)
		db.session.commit()

	def get_name(self):
		return self.name


########################
###### CAR MODEL ######
########################
class Car(db.Model, FormChoicesMixin):
	id = db.Column(db.Integer, primary_key=True)
	year = db.Column(db.String(4), index=True)
	names = db.relationship('CarLanguage', cascade='all, delete-orphan', 
							back_populates='car', lazy='dynamic')
	timestamp = db.Column(db.DateTime, default=datetime.utcnow)
	users = db.relationship('User', secondary=usercar_table,
			back_populates='cars', lazy='dynamic')

	def __repr__(self):
		return '<Car {}>'.format(self.get_name('en'))

	# Car names. 
	def set_name(self, language, name):
		self.names.append(CarLanguage(language, name))

	def get_name(self, lang_code='en', year=True):
		q = self.names.join('language').filter(Language.code==lang_code).first()
		# If it does not have a name for the selected language, give the default 'en'.
		if not q.name:
			q = self.names.join('language').filter(Language.code=='en').first() 
		# Return without year.
		if not self.year:
			return q.name
		# Return with year.
		return '|'.join((q.name, self.year)) if year else q.name

	# Related to api functional.
	def to_dict(self, lang_code='en'):
		data = {
			'id': self.id,
			'year': self.year,
			'users_count': self.users.count(),
			'_links': {
				'self': url_for('api.get_car', id=self.id)
			}
		}
		if lang_code != 'en':
			data['default_name'] = self.get_name(year=False)
		data['name'] = self.get_name(lang_code, False)
		return data

	def from_dict(self, data):
		pass



# Association table.
class CarLanguage(db.Model):
	__tablename__ = 'car_language'
	car_id = db.Column(db.Integer, db.ForeignKey('car.id'), primary_key=True)
	language_id = db.Column(db.Integer, db.ForeignKey('language.id'), primary_key=True)
	name = db.Column(db.String(124), index=True, nullable=False)
	car = db.relationship('Car', back_populates='names')
	language = db.relationship('Language', back_populates='cars')

	def __init__(self, language, name, **kwargs):
		super(CarLanguage, self).__init__(**kwargs)
		self.language = language
		self.name = name
	
	def __repr__(self):
		return '<CarLanguage {} {}>'.format(self.language.code, self.name)

	def get_language_code(self):
		return self.language.code


