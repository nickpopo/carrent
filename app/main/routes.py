from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from app import db
from app.models import User, Language
from .forms import EditProfileForm
from . import bp


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
	return render_template('index.html', title='Dashboard')


@bp.route('/user/<username>')
@login_required
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	return render_template('user.html', title='User Profile', user=user)


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