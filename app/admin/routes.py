from flask import render_template, request, url_for, flash, redirect, current_app
from flask_login import current_user, login_required
from app import db
from app.decorators import admin_required
from app.models import User, Car, Language, CarLanguage
from .forms import UserAddCarForm, CarForm
from . import bp


# Cars.
@bp.route('/cars')
@login_required
@admin_required
def cars():
	page = request.args.get('page', 1, type=int)
	cars = Car.query.order_by(Car.timestamp.desc()).paginate(
		page, current_app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('.cars', page=cars.next_num) \
		if cars.has_next else None
	prev_url = url_for('.cars', page=cars.prev_num) \
		if cars.has_prev else None
	return render_template('admin/cars.html', title='Cars', cars=cars.items,
						   next_url=next_url, prev_url=prev_url)


@bp.route('/cars/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_car():
	CarForm.add_fields()
	form = CarForm()
	if form.validate_on_submit():
		car = Car()
		# Сколько языков заполнено столько и создаем
		langs = Language.query.all()
		for key in form.data:
			if key in [lang.code for lang in langs]:
				lang = [lang for lang in langs if lang.code == key]
				car.names.append(CarLanguage(name=form.data[key], language=lang[0]))
		car.year = int(form.year.data)
		db.session.add(car)
		db.session.commit()
		flash('You successfuly create new car')
		return redirect(url_for('.cars'))

	return render_template('admin/create_car.html', title='Create new Car', form=form)


@bp.route('/cars/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_car(id):
	car = Car.query.first_or_404(id)
	CarForm.add_fields()
	form = CarForm()
	langs = Language.query.all()
	lang_codes = [lang.code for lang in langs]

	if form.validate_on_submit():
		# Получить объекты старые
			# Обновить
		# Сравнить старые с формой
			# Если есть новые
				# Добавить
		car_lang_codes = []
		for carlanguage in car.names:
			car_code = carlanguage.get_language_code()
			try:
				carlanguage.name = form[car_code].data
				car_lang_codes.append(car_code)
			except KeyError:
				db.session.delete(carlanguage)
		
		new_lang_code = set(lang_codes) - set(car_lang_codes)
		for new_code in new_lang_code:
			car.names.append(CarLanguage(name=form[new_code].data), language=new_code)

		car.year = int(form.year.data)
		db.session.add(car)
		db.session.commit()
		flash('You successfuly updated car')
		return redirect(url_for('.cars'))

	for code in lang_codes:
		form[code].data = car.get_name(code_lang=code, year=False)
	form.year.data = car.year

	return render_template('admin/edit_car.html', title='Edit Car', form=form)


@bp.route('/cars/delete/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_car(id):
	car = Car.query.first_or_404(id)
	name = car.get_name(code_lang='en', year=False)
	db.session.delete(car)
	db.session.commit()
	flash('Car {} was successfuly deleted.'.format(name))
	return redirect(url_for('.cars'))

# Users.
@bp.route('/users')
@login_required
@admin_required
def users():
	return 'TODO'


@bp.route('/user/<username>', methods=['GET', 'POST'])
@login_required
@admin_required
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	page = request.args.get('page', 1, type=int)
	cars = user.cars.order_by(Car.timestamp.desc()).paginate(
		page, current_app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('.user', page=cars.next_num) \
		if cars.has_next else None
	prev_url = url_for('.user', page=cars.prev_num) \
		if cars.has_prev else None

	form = UserAddCarForm()
	
	if form.validate_on_submit():
		car = Car.query.get(form.car.data)
		user.cars.append(car)
		db.session.commit()
		flash('Successfuly add {} to {}'.format(car.get_name(), user.username))
		return redirect(url_for('.user', username=user.username))

	return render_template('admin/user.html', title='User Profile', 
				user=user, form=form, cars=cars.items, next_url=next_url, prev_url=prev_url) 

