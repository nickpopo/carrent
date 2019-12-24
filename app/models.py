from hashlib import md5
from datetime import datetime
from time import time
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from app import db, login
from flask_login import UserMixin


class FormMixin(object):
	
	@classmethod
	def choices(cls):
		choices = []
		for obj in cls.query.all():
			choices.append((obj.id, obj.get_name()))
		return choices


class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	language_id = db.Column(db.Integer, db.ForeignKey('language.id'))
	language = db.relationship('Language', back_populates='users')
	cars = db.relationship('Car', secondary=lambda: usercar_table,
				back_populates='users', lazy='dynamic')

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

@login.user_loader
def load_user(id):
	return User.query.get(int(id))


usercar_table = db.Table('usercar', db.Model.metadata,
	db.Column('user_id', db.Integer, db.ForeignKey('user.id'),
			  primary_key=True),
	db.Column('car_id', db.Integer, db.ForeignKey('car.id'),
			  primary_key=True)
	)

class Language(db.Model, FormMixin):
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


class Car(db.Model, FormMixin):
	id = db.Column(db.Integer, primary_key=True)
	year = db.Column(db.String(4), index=True)
	names = db.relationship('CarLanguage', cascade='all, delete-orphan', 
							back_populates='car', lazy='dynamic')
	timestamp = db.Column(db.DateTime, default=datetime.utcnow)
	users = db.relationship('User', secondary=usercar_table,
			back_populates='cars', lazy='dynamic')

	def __repr__(self):
		return '<Car {}>'.format(self.get_name('en'))

	# Get car's name for particular language. 
	def get_name(self, code='en', year=True):
		q = self.names.join('language').filter(Language.code==code).one()
		if not q:
			return
		if not self.year:
			return q.name
		return '|'.join((q.name, self.year)) if year else q.name


# Association table.
class CarLanguage(db.Model):
	__tablename__ = 'car_language'
	car_id = db.Column(db.Integer, db.ForeignKey('car.id'), primary_key=True)
	language_id = db.Column(db.Integer, db.ForeignKey('language.id'), primary_key=True)
	name = db.Column(db.String(124), index=True, nullable=False)
	car = db.relationship('Car', back_populates='names')
	language = db.relationship('Language', back_populates='cars')


	def __init__(self, language, name):
		self.language = language
		self.name = name
	
	def __repr__(self):
		return '<CarLanguage {} {}>'.format(self.language.code, self.name)


