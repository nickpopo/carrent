from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from app import db
from app.models import User, Language, Car, CarLanguage
from .forms import EditProfileForm, CarForm, UserAddCarForm
from . import bp


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
	return render_template('index.html', title='Dashboard')


@bp.route('/explore')
@login_required
def explore():
	page = request.args.get('page', 1, type=int)
	cars = Car.query.order_by(Car.timestamp.desc()).paginate(
		page, current_app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('.explore', page=cars.next_num) \
		if cars.has_next else None
	prev_url = url_for('.explore', page=cars.prev_num) \
		if cars.has_prev else None
	return render_template('index.html', title='Explore', cars=cars.items,
						   next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>', methods=['GET', 'POST'])
@login_required
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

	return render_template('user.html', title='User Profile', 
				user=user, form=form, cars=cars.items, next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm(current_user.username)
	if form.validate_on_submit():
		current_user.username = form.username.data
		language = Language.query.get(int(form.language.data))
		if language:
			current_user.language = language
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('.edit_profile'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.language.data = current_user.language_id
	return render_template('edit_profile.html', title='Edit Profile', form=form)


@bp.route('/car/create', methods=['GET', 'POST'])
@login_required
def create_car():
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
		return redirect(url_for('.index'))

	return render_template('create_car.html', title='Create new Car', form=form)