from flask import render_template, request, url_for, flash, redirect, current_app
from flask_login import current_user, login_required
from app import db
from app.decorators import admin_required
from app.models import User, Car, Language, CarLanguage
from .forms import UserForm, EditUserProfileForm, UserAddCarForm, CarForm
from . import bp


# # # # # # # # # # # #
#  Routes for Users.  #
# # # # # # # # # # # #
@bp.route('/users')
@login_required
@admin_required
def users():
	page = request.args.get('page', 1, type=int)
	users = User.query.order_by(User.username.asc()).paginate(
		page, current_app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('.users', page=users.next_num) \
					   if users.has_next else None
	prev_url = url_for('.users', page=users.prev_num) \
					   if users.has_prev else None
	return render_template('admin/users.html', title='Explore Users', users=users.items, 
							next_url=next_url, prev_url=prev_url)


@bp.route('/user/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def user(id):
	user = User.query.get_or_404(id)
	page = request.args.get('page', 1, type=int)
	cars = user.cars.order_by(Car.timestamp.desc()).paginate(
		page, current_app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('.user', page=cars.next_num) \
		if cars.has_next else None
	prev_url = url_for('.user', page=cars.prev_num) \
		if cars.has_prev else None
	# Add selected car to user.
	form = UserAddCarForm(user_cars=user.cars.all())
	if form.validate_on_submit():
		car = Car.query.get(form.car.data)
		user.cars.append(car)
		db.session.commit()
		flash('Successfuly add {} to {}'.format(car.get_name(), user.username))
		return redirect(url_for('.user', id=user.id))
	elif request.method == 'GET':
		# Remove selected car from user.
		remove_car = request.args.get('remove_car')
		if remove_car:
			remove_car = Car.query.get_or_404(int(remove_car))
			user.cars.remove(remove_car)
			db.session.commit()
			return redirect(url_for('.user', id=user.id))
	if not form.car.choices:
		form = None
	return render_template('admin/user.html', title='User\'s Profile', 
				user=user, form=form, cars=cars.items, next_url=next_url, prev_url=prev_url) 


@bp.route('/user/edit_profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user_profile(id):
	user = User.query.get_or_404(id)
	form = EditUserProfileForm(original_username = user.username,
							   original_email = user.email)
	if form.validate_on_submit():
		user.username = form.username.data
		user.email = form.email.data
		user.language_id = int(form.language.data)
		user.role_id = form.role.data
		db.session.commit()
		flash('User\'s profile was successfuly updated.')
		return redirect(url_for('.user', id=user.id))

	form.username.data = user.username
	form.email.data = user.email
	form.language.data = user.language_id
	form.role.data = user.role_id
	return render_template('admin/edit_user_profile.html', title='Update user\'s profile', form=form)





@bp.route('/user/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
	form = UserForm()
	if form.validate_on_submit():
		user = User(
					username=form.username.data,
					email=form.email.data,
					language_id=int(form.language.data)
					)
		user.set_password(form.password.data)
		user.role_id = form.role.data
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you have added new user!')
		return redirect(url_for('.users'))

	return render_template('admin/create_user.html', title='Create new user', form=form)


@bp.route('/user/delete/<int:id>')
@login_required
@admin_required
def delete_user(id):
	user = User.query.get_or_404(id)
	username = user.username
	db.session.delete(user)
	db.session.commit()
	flash('User {} was successfuly deleted'.format(username))
	return redirect(url_for('.users'))



# # # # # # # # # # #
#  Routes for Cars. #
# # # # # # # # # # # 
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
	car = Car.query.get_or_404(id)
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


@bp.route('/cars/delete/<int:id>')
@login_required
@admin_required
def delete_car(id):
	car = Car.query.get_or_404(id)
	name = car.get_name(code_lang='en', year=False)
	db.session.delete(car)
	db.session.commit()
	flash('Car {} was successfuly deleted.'.format(name))
	return redirect(url_for('.cars'))

