from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from app import db
from app.models import User, Language, Car
from .forms import EditProfileForm
from . import bp
from app.decorators import admin_required


@bp.route('/')
@bp.route('/index')
@login_required
def index():
	page = request.args.get('page', 1, type=int)
	cars = current_user.cars.order_by(Car.timestamp.desc()).paginate(
		page, current_app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('.index', page=cars.next_num) \
		if cars.has_next else None
	prev_url = url_for('.index', page=cars.prev_num) \
		if cars.has_prev else None
	return render_template('index.html', title='Home', cars=cars.items,
						   next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	
	return render_template('user.html', title='User Profile', user=user)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	if current_app.config['ADMIN_LOCKED']:
		super_admin = User.query.filter_by(username='admin').first()
	if current_user == super_admin:
		flash('Super admin\'s profile is locked')
		return redirect(url_for('.user', username=current_user.username))
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