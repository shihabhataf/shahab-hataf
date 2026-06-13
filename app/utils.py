import os
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
