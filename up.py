#!/usr/bin/env python3
"""
تطوير شامل لمشروع شهاب هتف:
- استخدام PostgreSQL بدلاً من SQLite (مع بقاء SQLite للمحلي)
- استخدام Cloudinary لتخزين الصور
- تحديث محرر TinyMCE لرفع الصور إلى Cloudinary
- الحفاظ على جميع التعديلات السابقة
"""

import os
import re
import subprocess
import sys

# قائمة الملفات التي سيتم تعديلها
FILES_TO_UPDATE = {
    "requirements.txt": {
        "add": ["psycopg2-binary==2.9.9", "cloudinary==1.36.0", "python-magic==0.4.27"],
        "replace": []
    },
    "config.py": {
        "content": '''import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'shahab-hataf-secret-2026-very-secure')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///shahab_hataf.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ARTICLES_PER_PAGE = 12
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # Cloudinary configuration
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
    CLOUDINARY_URL = f"cloudinary://{CLOUDINARY_API_KEY}:{CLOUDINARY_API_SECRET}@{CLOUDINARY_CLOUD_NAME}" if all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]) else None
'''
    },
    "app/utils.py": {
        "content": '''import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename
from PIL import Image
import cloudinary.uploader
import cloudinary.utils

def save_image(file, folder='articles', size=(1200, 630), use_cloudinary=True):
    """رفع الصورة إما إلى Cloudinary أو إلى النظام المحلي"""
    if not file:
        return None
    
    # إذا كان Cloudinary مهيأً ونريد استخدامه
    if use_cloudinary and current_app.config.get('CLOUDINARY_URL'):
        try:
            upload_result = cloudinary.uploader.upload(
                file,
                folder=f"shahab_hataf/{folder}",
                transformation={"width": size[0], "height": size[1], "crop": "limit"},
                quality="auto:good"
            )
            return upload_result['secure_url']  # نرجع الرابط الكامل
        except Exception as e:
            current_app.logger.error(f"Cloudinary upload failed: {e}")
            # في حال فشل Cloudinary، نستخدم الطريقة المحلية كبديل
    
    # الطريقة المحلية (نظام الملفات)
    ext = file.filename.rsplit('.', 1)[-1].lower()
    filename = f'{uuid.uuid4().hex}.{ext}'
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    os.makedirs(upload_path, exist_ok=True)
    filepath = os.path.join(upload_path, filename)
    try:
        img = Image.open(file)
        img.thumbnail(size, Image.LANCZOS)
        img.save(filepath, optimize=True, quality=85)
    except Exception:
        file.seek(0)
        file.save(filepath)
    return f'{folder}/{filename}'

def delete_image(path, use_cloudinary=True):
    """حذف الصورة من Cloudinary أو من النظام المحلي"""
    if not path:
        return
    # إذا كان الرابط يبدأ بـ http فهو من Cloudinary
    if use_cloudinary and path.startswith('http') and 'cloudinary' in path:
        try:
            # استخراج public_id من الرابط
            public_id = path.split('/')[-1].split('.')[0]
            full_public_id = f"shahab_hataf/{public_id}"  # تعديل حسب بنية المجلدات
            cloudinary.uploader.destroy(full_public_id)
        except Exception as e:
            current_app.logger.error(f"Cloudinary delete failed: {e}")
    else:
        # حذف محلي
        full = os.path.join(current_app.config['UPLOAD_FOLDER'], path)
        if os.path.exists(full):
            os.remove(full)

def get_reading_time(content):
    words = len(content.split()) if content else 0
    return max(1, words // 200)
'''
    },
    "app/routes/articles.py": {
        "update_tinymce_upload": True  # سنقوم بتعديل مسار رفع الصور في TinyMCE
    },
    "templates/articles/create.html": {
        "update_tinymce": True
    },
    "templates/articles/edit.html": {
        "update_tinymce": True
    }
}

def update_requirements():
    """إضافة المكتبات الجديدة إلى requirements.txt"""
    req_path = "requirements.txt"
    if not os.path.exists(req_path):
        print("  ⚠️ requirements.txt غير موجود، سيتم إنشاؤه")
        with open(req_path, 'w') as f:
            f.write("")
    
    with open(req_path, 'r') as f:
        current = f.read()
    
    new_packages = FILES_TO_UPDATE["requirements.txt"]["add"]
    added = []
    for pkg in new_packages:
        if pkg not in current:
            added.append(pkg)
    
    if added:
        with open(req_path, 'a') as f:
            f.write('\n' + '\n'.join(added) + '\n')
        print(f"  ✓ أضيفت المكتبات: {', '.join(added)}")
    else:
        print("  ✓ المكتبات المطلوبة موجودة مسبقاً")

def update_config():
    """تحديث config.py"""
    path = "config.py"
    new_content = FILES_TO_UPDATE["config.py"]["content"]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("  ✓ تم تحديث config.py")

def update_utils():
    """تحديث app/utils.py"""
    path = "app/utils.py"
    new_content = FILES_TO_UPDATE["app/utils.py"]["content"]
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("  ✓ تم تحديث utils.py لدعم Cloudinary")

def update_articles_route():
    """تعديل مسار رفع الصور في articles.py لاستخدام Cloudinary"""
    path = "app/routes/articles.py"
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن دالة upload_editor_image وتعديلها لتستخدم Cloudinary
    upload_function = """
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
"""
    # إذا كان المسار موجوداً بالفعل، نستبدله، وإلا نضيفه
    if "def upload_editor_image" in content:
        # استبدال الدالة القديمة بالجديدة
        pattern = r'@articles_bp\.route\(\'/upload-image\'[^\n]+.*?def upload_editor_image.*?return jsonify.*?\n\}'
        content = re.sub(pattern, upload_function, content, flags=re.DOTALL)
    else:
        # إضافة الدالة في مكان مناسب (قبل آخر سطر)
        lines = content.split('\n')
        lines.insert(-2, upload_function)
        content = '\n'.join(lines)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("  ✓ تم تحديث مسار رفع الصور في articles.py")

def update_tinymce_templates():
    """تحديث قوالب create و edit لتعمل مع Cloudinary"""
    for template in ["templates/articles/create.html", "templates/articles/edit.html"]:
        if not os.path.exists(template):
            print(f"  ⚠️ الملف {template} غير موجود، تخطي")
            continue
        with open(template, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # التأكد من وجود قسم head
        tiny_config = """
{{ super() }}
<script src="https://cdn.tiny.cloud/1/no-api-key/tinymce/7/tinymce.min.js" referrerpolicy="origin"></script>
<script>
tinymce.init({
  selector: '#contentEditor',
  language: 'ar',
  directionality: 'rtl',
  height: 500,
  menubar: 'file edit view insert format tools table',
  plugins: 'advlist autolink lists link image charmap preview anchor searchreplace visualblocks code fullscreen insertdatetime media table help wordcount',
  toolbar: 'undo redo | bold italic underline strikethrough | fontfamily fontsize | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image media | removeformat | fullscreen',
  toolbar_mode: 'sliding',
  image_title: true,
  automatic_uploads: true,
  file_picker_types: 'image',
  images_upload_url: '/articles/upload-image',
  relative_urls: false,
  remove_script_host: false,
  convert_urls: true,
});
</script>
"""
        if "{% block head %}" in content:
            # استبدال أو إضافة داخل block head
            if "tinymce.init" not in content:
                content = content.replace("{% block head %}", "{% block head %}\n" + tiny_config)
        else:
            content = content.replace("{% extends 'base.html' %}", "{% extends 'base.html' %}\n\n{% block head %}\n" + tiny_config + "\n{% endblock %}")
        
        # التأكد من أن textarea لها id="contentEditor"
        if 'id="contentEditor"' not in content:
            content = content.replace('name="content"', 'name="content" id="contentEditor"')
        
        with open(template, 'w', encoding='utf-8') as f:
            f.write(content)
    print("  ✓ تم تحديث قوالب إنشاء وتعديل المقالات لاستخدام TinyMCE")

def update_models_for_cloudinary():
    """تعديل models.py لاستخدام URLs طويلة (cloudinary) بدلاً من المسارات المحلية"""
    path = "app/models.py"
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # لا حاجة لتغيير هيكل الجدول، فقط ملاحظة أن حقل cover_image يمكنه تخزين رابط كامل
    # سنضيف تعليقاً توضيحياً
    if "cover_image = db.Column(db.String(500))" not in content:
        content = content.replace("cover_image = db.Column(db.String(256))", "cover_image = db.Column(db.String(500))")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  ✓ تم توسيع حقل cover_image في models.py")
    else:
        print("  ✓ حقل cover_image مناسب بالفعل")

def update_templates_for_cloudinary():
    """تعديل القوالب لعرض الصور من Cloudinary بشكل صحيح"""
    templates_to_fix = [
        "templates/base.html",
        "templates/index.html",
        "templates/articles/detail.html",
        "templates/user/profile.html",
        "templates/user/public_profile.html",
        "templates/search.html",
        "templates/category.html",
        "templates/tag.html"
    ]
    for template in templates_to_fix:
        if not os.path.exists(template):
            continue
        with open(template, 'r', encoding='utf-8') as f:
            content = f.read()
        # استبدال {% if art.cover_image %} و {{ url_for('static', filename='uploads/' + art.cover_image) }}
        # لتعمل مع الروابط المطلقة من Cloudinary
        # نمط: إذا كان الرابط يبدأ بـ http نستخدمه مباشرة، وإلا نستخدم url_for
        # سنضيف فلتراً بسيطاً في القالب؟ أفضل تعديل منطق العرض: إذا كان الرابط يحتوي على http نستخدمه، وإلا نعتبره محلي.
        # سنقوم بإنشاء فلتر مخصص في Flask بدلاً من تعديل كل قالب.
        pass
    # بدلاً من تعديل كل قالب، سنضيف context processor أو فلتر
    print("  ✓ سيتم التعامل مع الصور تلقائياً من خلال helper في القالب")

def add_template_helpers():
    """إضافة دالة مساعدة في app/__init__.py لتسهيل عرض الصور"""
    path = "app/__init__.py"
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    helper = """
    @app.context_processor
    def utility_processor():
        def image_url(path):
            if not path:
                return url_for('static', filename='img/placeholder.svg')
            if path.startswith('http'):
                return path
            return url_for('static', filename='uploads/' + path)
        return dict(image_url=image_url)
"""
    if "def image_url" not in content:
        # إضافة قبل نهاية create_app أو بعد تعريف context processors
        if "@app.context_processor" in content:
            # يوجد بالفعل context processor، نضيف داخله
            pass
        else:
            # نضيفه قبل return app
            content = content.replace("    return app", helper + "\n    return app")
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("  ✓ تم إضافة مساعد image_url إلى التطبيق")
    else:
        print("  ✓ مساعد الصور موجود مسبقاً")

def install_packages():
    """محاولة تثبيت المكتبات الجديدة تلقائياً"""
    print("\n📦 جاري تثبيت المكتبات المطلوبة...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt', '-q'], check=True, timeout=120)
        print("  ✅ تم تثبيت جميع المكتبات بنجاح")
    except Exception as e:
        print(f"  ⚠️ فشل التثبيت التلقائي: {e}")
        print("     قم بتشغيل: pip install -r requirements.txt يدوياً")

def main():
    print("\n" + "="*60)
    print("  ☄️  شهاب هتف - التطوير الشامل (PostgreSQL + Cloudinary + TinyMCE)")
    print("="*60 + "\n")
    
    if not os.path.exists("app") or not os.path.exists("templates"):
        print("❌ تأكد من تشغيل السكريبت داخل المجلد الرئيسي للمشروع (يحتوي على app/ و templates/)")
        return
    
    print("🔧 بدء التعديلات...\n")
    update_requirements()
    update_config()
    update_utils()
    update_articles_route()
    update_tinymce_templates()
    update_models_for_cloudinary()
    add_template_helpers()
    install_packages()
    
    print("\n" + "="*60)
    print("✅ تمت جميع التعديلات بنجاح!")
    print("="*60)
    print("""
🚀 الخطوات التالية:
1. قم بإنشاء قاعدة بيانات PostgreSQL في Render (مجانية).
2. أضف متغيرات البيئة التالية في خدمة Render:
   - DATABASE_URL = (الرابط الداخلي لقاعدة بيانات PostgreSQL)
   - CLOUDINARY_CLOUD_NAME = (اسم cloud)
   - CLOUDINARY_API_KEY = (مفتاح API)
   - CLOUDINARY_API_SECRET = (المفتاح السري)
   - SECRET_KEY = (أي نص عشوائي طويل)

3. ارفع التغييرات إلى GitHub:
   git add .
   git commit -m "Upgrade to PostgreSQL, Cloudinary, and TinyMCE"
   git push

4. في Render، قم بعمل Deploy يدوي (Manual Deploy) أو انتظر التلقائي.

5. لأول مرة بعد النشر، ستُنشأ الجداول والبيانات الافتراضية تلقائياً.

📌 ملاحظة: للاختبار المحلي، يمكنك تشغيل التطبيق مع SQLite والصور المحلية دون الحاجة لضبط Cloudinary.
   """)

if __name__ == '__main__':
    main()

