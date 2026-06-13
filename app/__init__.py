from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object('config.Config')

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة'
    login_manager.login_message_category = 'warning'

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.articles import articles_bp
    from app.routes.admin import admin_bp
    from app.routes.user import user_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(articles_bp, url_prefix='/articles')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')

    # AJAX routes (like/save) لا تحتاج CSRF token في الـ header
    csrf.exempt(articles_bp)

    # ── Error handlers ──────────────────────────
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    # ── Context processors ───────────────────────
    @app.context_processor
    def inject_globals():
        from app.models import Category
        try:
            categories = Category.query.order_by(Category.name).all()
        except Exception:
            categories = []
        return dict(all_categories=categories)

    # ── Sitemap route ────────────────────────────
    @app.route('/sitemap.xml')
    def sitemap():
        from app.models import Article, Category
        from datetime import datetime
        from flask import Response, request
        base = request.host_url.rstrip('/')
        articles = Article.query.filter_by(status='published').all()
        categories = Category.query.all()
        lines = ['<?xml version="1.0" encoding="UTF-8"?>',
                 '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        lines.append(f'<url><loc>{base}/</loc><priority>1.0</priority></url>')
        for cat in categories:
            lines.append(f'<url><loc>{base}/category/{cat.slug}</loc><priority>0.8</priority></url>')
        for art in articles:
            dt = (art.published_at or art.created_at).strftime('%Y-%m-%d')
            lines.append(f'<url><loc>{base}/articles/{art.slug}</loc><lastmod>{dt}</lastmod><priority>0.7</priority></url>')
        lines.append('</urlset>')
        return Response('\n'.join(lines), mimetype='application/xml')

    # ── robots.txt ───────────────────────────────
    @app.route('/robots.txt')
    def robots():
        from flask import Response, request
        base = request.host_url.rstrip('/')
        txt = f"User-agent: *\nAllow: /\nDisallow: /admin/\nSitemap: {base}/sitemap.xml\n"
        return Response(txt, mimetype='text/plain')

    with app.app_context():
        db.create_all()
        _seed_data()

    return app


def _seed_data():
    from app.models import Category, User, Article, Tag
    from werkzeug.security import generate_password_hash
    from datetime import datetime, timedelta
    import random

    if Category.query.count() == 0:
        cats = [
            Category(name='تكنولوجيا', slug='technology', color='#6366f1', icon='⌨'),
            Category(name='رياضة',     slug='sports',     color='#10b981', icon='⚽'),
            Category(name='اقتصاد',   slug='economy',    color='#f59e0b', icon='⌶'),
            Category(name='سياسة',    slug='politics',   color='#ef4444', icon='⌂'),
            Category(name='ثقافة',    slug='culture',    color='#8b5cf6', icon='☯'),
            Category(name='صحة',      slug='health',     color='#06b6d4', icon='⚕'),
            Category(name='علوم',     slug='science',    color='#84cc16', icon='⚛'),
            Category(name='فن',       slug='art',        color='#f97316', icon='✎'),
        ]
        for c in cats:
            db.session.add(c)
        db.session.commit()

    if User.query.count() == 0:
        admin = User(
            username='admin',
            email='admin@shahab.com',
            full_name='مدير الموقع',
            password_hash=generate_password_hash('admin123'),
            is_admin=True,
            bio='مدير موقع شهاب هتف للأخبار والمقالات',
            is_verified=True,
            joined_at=datetime.utcnow()
        )
        db.session.add(admin)
        db.session.commit()

        tags_data = ['ذكاء اصطناعي', 'تقنية', 'أخبار', 'عالم', 'مستقبل', 'ابتكار', 'رقمي', 'صحة', 'رياضة', 'اقتصاد']
        tags = []
        for t in tags_data:
            from slugify import slugify
            tag = Tag(name=t, slug=slugify(t, allow_unicode=True))
            db.session.add(tag)
            tags.append(tag)
        db.session.commit()

        sample_articles = [
            {
                'title': 'الذكاء الاصطناعي يغير قواعد اللعبة في عالم الأعمال',
                'content': '''<p>يشهد عالم الأعمال اليوم ثورة حقيقية بفضل تقنيات الذكاء الاصطناعي التي باتت تتغلغل في كل القطاعات والصناعات.</p>
<p>من إدارة سلاسل التوريد إلى خدمة العملاء، تُحدث تقنيات الذكاء الاصطناعي نقلة نوعية في كيفية عمل الشركات وتفاعلها مع عملائها.</p>
<h2>تحويل قطاع التمويل</h2>
<p>في القطاع المالي، تستخدم البنوك الكبرى خوارزميات الذكاء الاصطناعي لاكتشاف الاحتيال في الوقت الفعلي، مما يوفر مليارات الدولارات سنوياً.</p>
<p>كما تتيح تقنيات التحليل التنبؤي للمستثمرين اتخاذ قرارات أكثر دقة وذكاءً، بناءً على بيانات ضخمة ومعقدة يصعب على الإنسان وحده تحليلها.</p>
<h2>الرعاية الصحية في عصر الذكاء الاصطناعي</h2>
<p>في مجال الصحة، تُساعد أنظمة الذكاء الاصطناعي الأطباء في تشخيص الأمراض بدقة غير مسبوقة، خاصةً في مجال الأشعة والتحاليل الطبية.</p>
<p>وقد أثبتت الدراسات أن بعض أنظمة الذكاء الاصطناعي تتفوق على الأطباء في اكتشاف بعض أنواع السرطانات في مراحلها المبكرة.</p>
<h2>مستقبل سوق العمل</h2>
<p>يتساءل كثيرون عن تأثير الذكاء الاصطناعي على سوق العمل، وما إذا كان سيُحل محل الوظائف البشرية أم سيخلق فرصاً جديدة.</p>
<p>يرى الخبراء أن الذكاء الاصطناعي سيُعيد تشكيل طبيعة العمل لا إلغاءه، مع ظهور مهن جديدة لم تكن موجودة من قبل.</p>''',
                'excerpt': 'يشهد عالم الأعمال اليوم ثورة حقيقية بفضل تقنيات الذكاء الاصطناعي التي باتت تتغلغل في كل القطاعات والصناعات.',
                'category_id': 1, 'status': 'published', 'is_featured': True, 'views': 1520,
            },
            {
                'title': 'كأس العالم 2026: توقعات المحللين وأبرز المنتخبات',
                'content': '''<p>مع اقتراب موعد كأس العالم 2026، يتسابق المحللون الرياضيون في تقديم توقعاتهم حول المنتخبات المرشحة للفوز باللقب.</p>
<p>تستضيف كلٌّ من الولايات المتحدة وكندا والمكسيك هذه النسخة التاريخية من البطولة الكبرى، في سابقة هي الأولى من نوعها بمشاركة ثلاث دول مضيفة.</p>
<h2>المنتخبات المرشحة</h2>
<p>تتصدر قائمة المرشحين منتخبات كالبرازيل وفرنسا وإنجلترا وإسبانيا وألمانيا، إضافة إلى مفاجآت محتملة من أمريكا الجنوبية وأفريقيا.</p>
<p>يرى كثير من المحللين أن منتخب البرازيل يدخل البطولة بزخم كبير بعد سنوات من إعادة البناء والتجديد.</p>
<h2>المجموعات والمباريات</h2>
<p>تُقام البطولة في 16 مدينة أمريكية وكندية ومكسيكية، مما يجعلها الأوسع جغرافياً في تاريخ كأس العالم.</p>''',
                'excerpt': 'مع اقتراب موعد كأس العالم 2026، يتسابق المحللون الرياضيون في تقديم توقعاتهم حول المنتخبات المرشحة.',
                'category_id': 2, 'status': 'published', 'is_featured': True, 'views': 2340,
            },
            {
                'title': 'الاقتصاد العالمي في 2026: تحديات وفرص',
                'content': '''<p>يمر الاقتصاد العالمي بمرحلة دقيقة تجمع بين التحديات الكبيرة والفرص الواعدة في آنٍ واحد.</p>
<p>بعد سنوات من التقلبات الحادة والاضطرابات المتكررة، يبدو أن الاقتصاد العالمي يسير نحو استقرار نسبي، وإن كانت مخاطر جدية لا تزال تحدق به.</p>
<h2>التضخم والسياسات النقدية</h2>
<p>شكّل التضخم التحدي الأكبر للاقتصادات الكبرى خلال السنوات الأخيرة، مما دفع البنوك المركزية إلى رفع أسعار الفائدة بشكل متتالٍ وغير مسبوق.</p>
<p>اليوم، بدأت معدلات التضخم في التراجع في معظم الدول المتقدمة، مما فتح الباب أمام تخفيف السياسات النقدية تدريجياً.</p>
<h2>الاقتصادات الناشئة</h2>
<p>تبرز الاقتصادات الناشئة كمحرك رئيسي للنمو العالمي، ولا سيما في جنوب وجنوب شرق آسيا وبعض دول أفريقيا جنوب الصحراء.</p>''',
                'excerpt': 'يمر الاقتصاد العالمي بمرحلة دقيقة تجمع بين التحديات الكبيرة والفرص الواعدة في آنٍ واحد.',
                'category_id': 3, 'status': 'published', 'is_featured': False, 'views': 980,
            },
            {
                'title': 'ثورة الطاقة المتجددة: نحو مستقبل أخضر',
                'content': '''<p>تشهد صناعة الطاقة تحولاً جذرياً غير مسبوق، إذ باتت مصادر الطاقة المتجددة تنافس بشكل جدي الوقود الأحفوري التقليدي.</p>
<p>انخفضت تكاليف الطاقة الشمسية وطاقة الرياح بشكل دراماتيكي خلال العقد الماضي، مما جعلها الخيار الأرخص في كثير من مناطق العالم.</p>
<h2>الطاقة الشمسية تقود الثورة</h2>
<p>تتصدر الطاقة الشمسية قائمة مصادر الطاقة المتجددة نمواً وانتشاراً، حيث تضاعفت القدرات المركبة عالمياً عدة مرات خلال السنوات الأخيرة.</p>
<h2>التحديات التقنية</h2>
<p>رغم التقدم الهائل، لا تزال ثمة تحديات تواجه الطاقة المتجددة، أبرزها مشكلة التخزين والانقطاع المرتبط بأحوال الطقس.</p>''',
                'excerpt': 'تشهد صناعة الطاقة تحولاً جذرياً غير مسبوق، إذ باتت مصادر الطاقة المتجددة تنافس بشكل جدي الوقود الأحفوري.',
                'category_id': 7, 'status': 'published', 'is_featured': True, 'views': 1750,
            },
            {
                'title': 'الصحة النفسية في العصر الرقمي: تحديات وحلول',
                'content': '''<p>باتت الصحة النفسية في مقدمة اهتمامات المجتمع الحديث، لا سيما في ظل التحولات الرقمية المتسارعة التي تفرض ضغوطاً جديدة ومتنوعة.</p>
<p>تكشف الدراسات الحديثة عن ارتباط وثيق بين الاستخدام المفرط للتكنولوجيا ووسائل التواصل الاجتماعي وتراجع مستويات الصحة النفسية.</p>
<h2>وسائل التواصل والصحة النفسية</h2>
<p>أثبتت أبحاث عديدة أن الاستخدام المفرط لوسائل التواصل الاجتماعي يرتبط بزيادة مشاعر القلق والاكتئاب والوحدة.</p>
<h2>حلول عملية</h2>
<p>يوصي الخبراء بتحديد أوقات استخدام التقنية، وممارسة الأنشطة البدنية، والحفاظ على علاقات اجتماعية حقيقية.</p>''',
                'excerpt': 'باتت الصحة النفسية في مقدمة اهتمامات المجتمع الحديث في ظل التحولات الرقمية المتسارعة.',
                'category_id': 6, 'status': 'published', 'is_featured': False, 'views': 1230,
            },
            {
                'title': 'الفن العربي المعاصر: هوية وإبداع',
                'content': '''<p>يشهد الفن العربي المعاصر ازدهاراً لافتاً على الصعيدين المحلي والعالمي، مع تنامي حضور الفنانين العرب في أبرز المعارض والمزادات الدولية.</p>
<p>يتميز هذا الفن بقدرته الفريدة على الجمع بين الموروث الحضاري العميق ومتطلبات التعبير الإبداعي في العصر الحديث.</p>
<h2>أصوات جديدة على الساحة</h2>
<p>برز جيل جديد من الفنانين العرب الذين يقدمون رؤى إبداعية مستقلة وجريئة، تتحدى القوالب التقليدية وتفتح آفاقاً جديدة للتعبير الفني.</p>
<h2>الفن الرقمي والعالم العربي</h2>
<p>أسهمت التقنيات الرقمية في توسيع نطاق التعبير الفني وإتاحة الفرص أمام مواهب شابة لم تكن لتصل إلى العالمية بالوسائل التقليدية.</p>''',
                'excerpt': 'يشهد الفن العربي المعاصر ازدهاراً لافتاً على الصعيدين المحلي والعالمي مع تنامي حضور الفنانين العرب.',
                'category_id': 8, 'status': 'published', 'is_featured': False, 'views': 870,
            },
            {
                'title': 'السياسة الدولية في عالم متغير',
                'content': '''<p>يشهد النظام الدولي تحولات عميقة تعيد رسم خارطة القوى والتحالفات بصورة لم تُشهد منذ نهاية الحرب الباردة.</p>
<p>تتصاعد حدة التنافس بين القوى الكبرى، وتتعدد بؤر التوتر الإقليمية، في مشهد دولي يزداد تعقيداً وترابطاً في الوقت ذاته.</p>
<h2>التعددية القطبية</h2>
<p>تتراجع الأحادية القطبية التي سادت العالم في أعقاب الحرب الباردة، لتحل محلها تعددية قطبية تُشكّل فيها قوى كالصين والهند وروسيا وأوروبا أدواراً محورية.</p>
<h2>التحالفات الجديدة</h2>
<p>أفرز هذا الواقع الجديد تحالفات وشراكات غير مسبوقة تتجاوز الحدود الأيديولوجية التقليدية، مدفوعةً بالمصالح الاقتصادية والأمنية المتشابكة.</p>''',
                'excerpt': 'يشهد النظام الدولي تحولات عميقة تعيد رسم خارطة القوى والتحالفات بصورة لم تُشهد منذ نهاية الحرب الباردة.',
                'category_id': 4, 'status': 'published', 'is_featured': False, 'views': 1100,
            },
            {
                'title': 'التراث الثقافي العربي في مواجهة العولمة',
                'content': '''<p>يقف التراث الثقافي العربي عند مفترق طرق حاسم، في مواجهة موجة العولمة الجارفة التي تُسوّي الفوارق وتُذيب الخصوصيات.</p>
<p>بين من يرى في الانفتاح فرصة للإثراء والتجديد، ومن يخشى فيه خطر الاندثار والضياع، تتواصل النقاشات الساخنة حول مستقبل الهوية الثقافية العربية.</p>
<h2>اللغة العربية في العصر الرقمي</h2>
<p>تواجه اللغة العربية تحديات جسيمة في عصر الإنترنت والتواصل الاجتماعي، غير أن ثمة مبادرات واعدة تسعى إلى تعزيز حضورها الرقمي.</p>
<h2>الموروث الشعبي والهوية</h2>
<p>يمثل الموروث الشعبي من موسيقى وشعر وفنون تقليدية ركيزة أساسية في بناء الهوية الثقافية وصون الذاكرة الجمعية للشعوب العربية.</p>''',
                'excerpt': 'يقف التراث الثقافي العربي عند مفترق طرق حاسم في مواجهة موجة العولمة الجارفة.',
                'category_id': 5, 'status': 'published', 'is_featured': True, 'views': 960,
            },
        ]

        from slugify import slugify

        for i, art_data in enumerate(sample_articles):
            slug = slugify(art_data['title'], allow_unicode=True)
            base_slug = slug
            counter = 1
            while Article.query.filter_by(slug=slug).first():
                slug = f'{base_slug}-{counter}'
                counter += 1
            art = Article(
                title=art_data['title'],
                slug=slug,
                content=art_data['content'],
                excerpt=art_data['excerpt'],
                author_id=admin.id,
                category_id=art_data['category_id'],
                status=art_data['status'],
                is_featured=art_data['is_featured'],
                views=art_data['views'],
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                published_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            )
            if tags:
                art.tags.append(random.choice(tags))
            db.session.add(art)

        db.session.commit()
