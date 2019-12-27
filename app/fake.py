from datetime import datetime
from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from app import db
from app.models import User, Car, CarLanguage, Language


car_names = [
('Audi', 'Ауди'),
('BMW', 'Бумер'),
('Nissan', 'Нисан'),
('Lada', 'Лада'),
('Honda', 'Хонда'),
('Ford', 'Форд'),
('Cadilac', 'Кадилак')
]


def users(count=100):
	fake = Faker()
	i = 0
	lang_count = Language.query.count()
	while i < int(count):
		u = User(username=fake.user_name(),
				 email=fake.email()
		)
		u.language = Language.query.offset(randint(0, lang_count - 1)).first()
		u.set_password('password')
		db.session.add(u)
		try:
			db.session.commit()
			i += 1
		except IntegrityError:
			db.session.rollback()
	print('{} fake users were successfully created.'.format(i))

def cars(count=100):
	fake = Faker()
	i = 0
	user_count = User.query.count()
	langs = Language.query.all()
	car_names_len = len(car_names)
	while i < int(count):
		u = User.query.offset(randint(0, user_count - 1)).first()
		c = Car()
		c.year = randint(1970, datetime.now().year)
		c.timestamp = fake.past_date()
		c.users.append(u)
		for lang in langs:
			if lang.code == 'en':
				c.set_name(lang, car_names[randint(0, car_names_len - 1)][0])
			elif lang.code == 'ru':
				c.set_name(lang, car_names[randint(0, car_names_len - 1)][1])
		db.session.add(c)
		try:
			db.session.commit()
			i += 1
		except IntegrityError:
			db.session.rollback()
		print('{} fake cars were successfully created.'.format(i))