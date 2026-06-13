from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app.models import Article, Category, Tag, Comment, Like, SavedArticle
from app.forms import ArticleForm, CommentForm
from app.utils import save_image, delete_image
from app import db
from slugify import slugify
from datetime import datetime
from werkzeug.datastructures import FileStorage

articles_bp = Blueprint('articles', __name__)

@articles_bp.route('/<slug>')
def detail(slug):
    article = Article.query.filter_by(slug=slug, status='published').first_or_404()
    article.views += 1
    db.session.commit()
    related = Article.query.filter(
        Article.category_id == article.category_id,
        Article.id != article.id,
        Article.status == 'published'
    ).order_by(Article.published_at.desc()).limit(4).all()
    comments = article.comments.filter_by(is_approved=True).order_by(Comment.created_at.desc()).all()
    comment_form = CommentForm()
    user_liked = current_user.is_authenticated and current_user.has_liked(article)
    user_saved = current_user.is_authenticated and current_user.has_saved(article)
    return render_template('articles/detail.html', article=article, related=related,
                           comments=comments, comment_form=comment_form,
                           user_liked=user_liked, user_saved=user_saved)

@articles_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.is_admin:
        abort(403)
    form = ArticleForm()
    categories = Category.query.all()
    form.category_id.choices = [(0, 'بدون تصنيف')] + [(c.id, c.name) for c in categories]
    if form.validate_on_submit():
        slug = slugify(form.title.data, allow_unicode=True)
        base_slug = slug
        counter = 1
        while Article.query.filter_by(slug=slug).first():
            slug = f'{base_slug}-{counter}'
            counter += 1
        cover_path = None
        cover_file = form.cover_image.data
        if cover_file and isinstance(cover_file, FileStorage) and cover_file.filename:
            cover_path = save_image(cover_file)
        article = Article(
            title=form.title.data,
            slug=slug,
            content=form.content.data,
            excerpt=form.excerpt.data or form.content.data[:200],
            cover_image=cover_path,
            youtube_url=form.youtube_url.data or None,
            author_id=current_user.id,
            category_id=form.category_id.data if form.category_id.data else None,
            status=form.status.data,
            published_at=datetime.utcnow() if form.status.data == 'published' else None
        )
        if form.tags.data:
            for tag_name in form.tags.data.split(','):
                tag_name = tag_name.strip()
                if tag_name:
                    tag_slug = slugify(tag_name, allow_unicode=True)
                    tag = Tag.query.filter_by(slug=tag_slug).first()
                    if not tag:
                        tag = Tag(name=tag_name, slug=tag_slug)
                        db.session.add(tag)
                    article.tags.append(tag)
        db.session.add(article)
        db.session.commit()
        flash('تم نشر المقال بنجاح!', 'success')
        return redirect(url_for('articles.detail', slug=article.slug))
    return render_template('articles/create.html', form=form, categories=categories)

@articles_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    article = Article.query.get_or_404(id)
    if article.author_id != current_user.id and not current_user.is_admin:
        abort(403)
    form = ArticleForm(obj=article)
    categories = Category.query.all()
    form.category_id.choices = [(0, 'بدون تصنيف')] + [(c.id, c.name) for c in categories]
    if form.validate_on_submit():
        article.title = form.title.data
        article.content = form.content.data
        article.excerpt = form.excerpt.data
        article.youtube_url = form.youtube_url.data or None
        article.category_id = form.category_id.data if form.category_id.data else None
        article.status = form.status.data
        if form.status.data == 'published' and not article.published_at:
            article.published_at = datetime.utcnow()
        
        # التحقق من رفع صورة جديدة
        cover_file = form.cover_image.data
        if cover_file and isinstance(cover_file, FileStorage) and cover_file.filename:
            delete_image(article.cover_image)
            article.cover_image = save_image(cover_file)
        
        article.tags = []
        if form.tags.data:
            for tag_name in form.tags.data.split(','):
                tag_name = tag_name.strip()
                if tag_name:
                    tag_slug = slugify(tag_name, allow_unicode=True)
                    tag = Tag.query.filter_by(slug=tag_slug).first()
                    if not tag:
                        tag = Tag(name=tag_name, slug=tag_slug)
                        db.session.add(tag)
                    article.tags.append(tag)
        db.session.commit()
        flash('تم تحديث المقال بنجاح!', 'success')
        return redirect(url_for('articles.detail', slug=article.slug))
    form.tags.data = ', '.join([t.name for t in article.tags])
    return render_template('articles/edit.html', form=form, article=article, categories=categories)

@articles_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    article = Article.query.get_or_404(id)
    if article.author_id != current_user.id and not current_user.is_admin:
        abort(403)
    delete_image(article.cover_image)
    db.session.delete(article)
    db.session.commit()
    flash('تم حذف المقال', 'success')
    return redirect(url_for('main.index'))

@articles_bp.route('/<int:id>/comment', methods=['POST'])
@login_required
def comment(id):
    article = Article.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        c = Comment(content=form.content.data, author_id=current_user.id, article_id=article.id)
        db.session.add(c)
        db.session.commit()
        flash('تم إضافة تعليقك!', 'success')
    return redirect(url_for('articles.detail', slug=article.slug))

@articles_bp.route('/<int:id>/like', methods=['POST'])
@login_required
def like(id):
    article = Article.query.get_or_404(id)
    existing = Like.query.filter_by(user_id=current_user.id, article_id=id).first()
    if existing:
        db.session.delete(existing)
        liked = False
    else:
        db.session.add(Like(user_id=current_user.id, article_id=id))
        liked = True
    db.session.commit()
    return jsonify({'liked': liked, 'count': article.likes_count})

@articles_bp.route('/<int:id>/save', methods=['POST'])
@login_required
def save_article(id):
    article = Article.query.get_or_404(id)
    existing = SavedArticle.query.filter_by(user_id=current_user.id, article_id=id).first()
    if existing:
        db.session.delete(existing)
        saved = False
    else:
        db.session.add(SavedArticle(user_id=current_user.id, article_id=id))
        saved = True
    db.session.commit()

@articles_bp.route('/upload-image', methods=['POST'])
@login_required
def upload_editor_image():
    from flask import request, jsonify, current_app
    from app.utils import save_image
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    try:
        url = save_image(file, folder='editor_images', size=(1920, 1080))
        # إذا كان save_image أرجع رابط Cloudinary كامل، استخدمه مباشرة
        return jsonify({'location': url})
    except Exception as e:
        current_app.logger.error(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500

    return jsonify({'saved': saved})
