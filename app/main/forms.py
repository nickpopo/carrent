from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from flask_wtf import FlaskForm
from app.models import User, Language

class EditProfileForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	language = SelectField('Language', coerce=int, validators=[DataRequired()])
	submit = SubmitField('Submit')


	def __init__(self, original_username, *args, **kwargs):
		super(EditProfileForm, self).__init__(*args, **kwargs)
		self.original_username = original_username
		# Populate choices of language.
		self.language.choices = Language.choices()


	def validate_username(self, username):
		if username.data != self.original_username:
			user = User.query.filter_by(username=self.username.data).first()
			if user is not None:
				raise ValidationError('Please use a different username.')