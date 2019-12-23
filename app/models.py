from hashlib import md5
from datetime import datetime
from time import time
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from app import db, login
from flask_login import UserMixin


class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	language_id = db.Column(db.Integer, db.ForeignKey('language.id'))
	language = db.relationship('Language', back_populates='users')
	
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


class Language(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	code = db.Column(db.String(5), unique=True)
	users = db.relationship('User', back_populates='language')

	@classmethod
	def choices(cls):
		choices = []
		for obj in cls.query.all():
			choices.append((obj.id, obj.name))
		return choices

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