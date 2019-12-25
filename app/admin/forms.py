from datetime import datetime
from wtforms import StringField, SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired, NumberRange
from flask_wtf import FlaskForm
from app.models import User, Language, Car


class UserAddCarForm(FlaskForm):
	car = SelectField('Car', coerce=int, validators=[DataRequired()])
	submit = SubmitField('Add Car')

	def __init__(self, *args, **kwargs):
		super(UserAddCarForm, self).__init__(*args, **kwargs)
		self.car.choices = Car.choices()


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