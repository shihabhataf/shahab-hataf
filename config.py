import os
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
