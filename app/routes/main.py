from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app.models import Article, Category, Tag, User
from app import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    featured = Article.query.filter_by(status='published', is_featured=True).order_by(Article.published_at.desc()).limit(5).all()
    latest = Article.query.filter_by(status='published').order_by(Article.published_at.desc()).limit(8).all()
    popular = Article.query.filter_by(status='published').order_by(Article.views.desc()).limit(6).all()
    categories = Category.query.all()
    return render_template('index.html', featured=featured, latest=latest, popular=popular, categories=categories)

@main_bp.route('/search')
@main_bp.route('/search')
def search():
    q = request.args.get('q', '').strip()
    cat_slug = request.args.get('cat', '')
    page = request.args.get('page', 1, type=int)
    results = []
    total = 0
    selected_cat = None
    if q:
        from app.models import Category
        query = Article.query.filter(Article.status == 'published')
        if cat_slug:
            category = Category.query.filter_by(slug=cat_slug).first()
            if category:
                selected_cat = cat_slug
                query = query.filter(Article.category_id == category.id)
        query = query.filter(
            db.or_(
                Article.title.contains(q),
                Article.content.contains(q),
                Article.excerpt.contains(q)
            )
        ).order_by(Article.published_at.desc())
        total = query.count()
        results = query.paginate(page=page, per_page=10)
    return render_template('search.html', results=results, q=q, total=total, selected_cat=selected_cat)

@main_bp.route('/category/<slug>')
def category(slug):
    from app.models import Category
    cat = Category.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    articles = Article.query.filter_by(status='published', category_id=cat.id).order_by(Article.published_at.desc()).paginate(page=page, per_page=12)
    return render_template('category.html', category=cat, articles=articles)

@main_bp.route('/tag/<slug>')
def tag(slug):
    tag = Tag.query.filter_by(slug=slug).first_or_404()
    page = request.args.get('page', 1, type=int)
    articles = tag.articles.filter_by(status='published').order_by(Article.published_at.desc()).paginate(page=page, per_page=12)
    return render_template('tag.html', tag=tag, articles=articles)
