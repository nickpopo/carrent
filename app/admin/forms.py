from datetime import datetime
from wtforms import StringField, SelectField, PasswordField, SubmitField, \
	IntegerField
from wtforms.validators import DataRequired, NumberRange, ValidationError, \
	EqualTo, Email, Regexp, Length
from flask_wtf import FlaskForm
from app.models import User, Language, Car, Role


class UserForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	language = SelectField('Language', coerce=int, validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
	role = SelectField('Role', coerce=int, validators=[DataRequired()])
	submit = SubmitField('Register')

	# Populate choices of language.
	def __init__(self, *args, **kwargs):
		super(UserForm, self).__init__(*args, **kwargs)
		self.language.choices = Language.choices()
		self.role.choices = Role.choices()

	# Create custom validators. 
	# Pattern validate_<field_name>, WTForms takes those pattern as custom validators 
	# and invokes them in addition to the stock validators.
	# Ensure username is available.
	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('Please use a differnet username.')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('Please use a different email address.')


class EditUserProfileForm(FlaskForm):
	username = StringField('Username', validators=[
		DataRequired(), Length(1, 64),
		Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
			   'Usernames must have only letters, numbers, dots or '
			   'underscores')])
	email = StringField('Email', validators=[DataRequired(), Email()])
	language = SelectField('Language', coerce=int, validators=[DataRequired()])
	role = SelectField('Role', coerce=int, validators=[DataRequired()])
	submit = SubmitField('Update')

	def __init__(self, original_username, original_email, *args, **kwargs):
		super(EditUserProfileForm, self).__init__(*args, **kwargs)
		self.original_username = original_username
		self.original_email = original_email
		self.language.choices = Language.choices()
		self.role.choices = Role.choices()

	# Create custom validators. 
	# Pattern validate_<field_name>, WTForms takes those pattern as custom validators 
	# and invokes them in addition to the stock validators.
	# Ensure username is available.
	def validate_username(self, username):
		if  username.data != self.original_username:
			user = User.query.filter_by(username=username.data).first()
			if user is not None:
				raise ValidationError('Please use a differnet username.')

	def validate_email(self, email):
		if  email.data != self.original_email:
			user = User.query.filter_by(email=email.data).first()
			if user is not None:
				raise ValidationError('Please use a different email address.')


class UserAddCarForm(FlaskForm):
	car = SelectField('Car', coerce=int, validators=[DataRequired()])
	submit = SubmitField('Add Car')

	def __init__(self, user_cars, *args, **kwargs):
		super(UserAddCarForm, self).__init__(*args, **kwargs)
		user_cars = [(car.id, car.get_name()) for car in user_cars]
		choices = Car.choices()
		for car in user_cars:
			if car in choices:
				choices.remove(car)
		self.car.choices = choices


class CarForm(FlaskForm):
	fields_added = False
	
	@classmethod
	def add_fields(cls):
		if cls.fields_added:
			return
		# Add dynamic fields.
		langs = Language.query.all()
		for lang in langs:
			if lang.code == 'en':
				setattr(cls, lang.code, StringField(f'{lang.name} name', validators=[DataRequired()]))
			else:
				setattr(cls, lang.code, StringField(f'{lang.name} name'))

		setattr(cls, 'year', IntegerField('Built Year', validators=[DataRequired(), NumberRange(min=1900, max=datetime.now().year)]))
		setattr(cls, 'submit', SubmitField('Submit'))

		cls.fields_added = True