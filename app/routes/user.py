from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.datastructures import FileStorage
from app.models import User, Article, SavedArticle
from app.forms import ProfileForm
from app.utils import save_image
from app import db

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile')
@login_required
def profile():
    articles = current_user.articles.filter_by(status='published').order_by(Article.created_at.desc()).all()
    drafts = current_user.articles.filter_by(status='draft').order_by(Article.created_at.desc()).all()
    saved = SavedArticle.query.filter_by(user_id=current_user.id).order_by(SavedArticle.saved_at.desc()).all()
    return render_template('user/profile.html', articles=articles, drafts=drafts, saved=saved)

@user_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        if form.current_password.data:
            if not check_password_hash(current_user.password_hash, form.current_password.data):
                flash('كلمة المرور الحالية غير صحيحة', 'danger')
                return render_template('user/settings.html', form=form)
            if form.new_password.data:
                current_user.password_hash = generate_password_hash(form.new_password.data)
        current_user.full_name = form.full_name.data
        current_user.bio = form.bio.data
        
        # التحقق من صحة ملف الصورة
        avatar_file = form.avatar.data
        if avatar_file and hasattr(avatar_file, 'filename') and avatar_file.filename:
            current_user.avatar = save_image(avatar_file, folder='avatars', size=(400, 400))
        
        db.session.commit()
        flash('تم تحديث الملف الشخصي!', 'success')
        return redirect(url_for('user.profile'))
    return render_template('user/settings.html', form=form)

@user_bp.route('/<username>')
def public_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    articles = user.articles.filter_by(status='published').order_by(Article.published_at.desc()).all()
    return render_template('user/public_profile.html', profile_user=user, articles=articles)
