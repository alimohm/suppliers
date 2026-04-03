import os

class Config:
    # سر التشفير للجلسات
    SECRET_KEY = os.environ.get('SK', 'MAHJOUB_ROYAL_2026')
    
    # الربط الذكي: إذا لم يجد DATABASE_URL (في Railway)، سيستخدم sqlite محلياً للتجربة
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # قاعدة بيانات مؤقتة للجهاز المحلي لضمان عدم توقف الكود
        SQLALCHEMY_DATABASE_URI = 'sqlite:///mahjoub_local.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- إعدادات الميديا ورفع الملفات ---
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
