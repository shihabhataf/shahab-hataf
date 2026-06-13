from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models import Article, User, Category, Comment, Tag, Like, SavedArticle
from app.forms import CategoryForm
from app import db
from functools import wraps
from slugify import slugify

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return login_required(decorated)

@admin_bp.route('/')
@admin_required
def dashboard():
    stats = {
        'articles': Article.query.filter_by(status='published').count(),
        'drafts': Article.query.filter_by(status='draft').count(),
        'users': User.query.count(),
        'comments': Comment.query.count(),
        'categories': Category.query.count(),
        'total_views': db.session.query(db.func.sum(Article.views)).scalar() or 0,
        'total_likes': Like.query.count(),
        'saved': SavedArticle.query.count(),
    }
    latest_articles = Article.query.order_by(Article.created_at.desc()).limit(10).all()
    latest_users = User.query.order_by(User.joined_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats, latest_articles=latest_articles, latest_users=latest_users)

@admin_bp.route('/articles')
@admin_required
def articles():
    page = request.args.get('page', 1, type=int)
    arts = Article.query.order_by(Article.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/articles.html', articles=arts)

@admin_bp.route('/articles/<int:id>/toggle-featured', methods=['POST'])
@admin_required
def toggle_featured(id):
    art = Article.query.get_or_404(id)
    art.is_featured = not art.is_featured
    db.session.commit()
    return redirect(url_for('admin.articles'))

@admin_bp.route('/articles/<int:id>/delete', methods=['POST'])
@admin_required
def delete_article(id):
    art = Article.query.get_or_404(id)
    db.session.delete(art)
    db.session.commit()
    flash('تم حذف المقال', 'success')
    return redirect(url_for('admin.articles'))

@admin_bp.route('/users')
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    all_users = User.query.order_by(User.joined_at.desc()).paginate(page=page, per_page=20)
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/users/<int:id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_admin(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('لا يمكنك تغيير صلاحياتك الخاصة', 'warning')
    else:
        user.is_admin = not user.is_admin
        db.session.commit()
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:id>/toggle-active', methods=['POST'])
@admin_required
def toggle_active(id):
    user = User.query.get_or_404(id)
    if user.id != current_user.id:
        user.is_active = not user.is_active
        db.session.commit()
    return redirect(url_for('admin.users'))

@admin_bp.route('/comments')
@admin_required
def comments():
    page = request.args.get('page', 1, type=int)
    all_comments = Comment.query.order_by(Comment.created_at.desc()).paginate(page=page, per_page=30)
    return render_template('admin/comments.html', comments=all_comments)

@admin_bp.route('/comments/<int:id>/toggle', methods=['POST'])
@admin_required
def toggle_comment(id):
    c = Comment.query.get_or_404(id)
    c.is_approved = not c.is_approved
    db.session.commit()
    return redirect(url_for('admin.comments'))

@admin_bp.route('/comments/<int:id>/delete', methods=['POST'])
@admin_required
def delete_comment(id):
    c = Comment.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    return redirect(url_for('admin.comments'))

@admin_bp.route('/categories', methods=['GET', 'POST'])
@admin_required
def categories():
    form = CategoryForm()
    if form.validate_on_submit():
        sl = slugify(form.name.data, allow_unicode=True)
        cat = Category(name=form.name.data, slug=sl, description=form.description.data,
                       color=form.color.data or '#6366f1', icon=form.icon.data or '📰')
        db.session.add(cat)
        db.session.commit()
        flash('تم إضافة التصنيف', 'success')
        return redirect(url_for('admin.categories'))
    all_cats = Category.query.all()
    return render_template('admin/categories.html', categories=all_cats, form=form)

@admin_bp.route('/categories/<int:id>/delete', methods=['POST'])
@admin_required
def delete_category(id):
    cat = Category.query.get_or_404(id)
    db.session.delete(cat)
    db.session.commit()
    flash('تم حذف التصنيف', 'success')
    return redirect(url_for('admin.categories'))

@admin_bp.route('/tags')
@admin_required
def tags():
    all_tags = Tag.query.all()
    return render_template('admin/tags.html', tags=all_tags)

@admin_bp.route('/tags/<int:id>/delete', methods=['POST'])
@admin_required
def delete_tag(id):
    tag = Tag.query.get_or_404(id)
    db.session.delete(tag)
    db.session.commit()
    return redirect(url_for('admin.tags'))
