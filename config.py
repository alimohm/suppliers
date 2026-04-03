import os

class Config:
    # قراءة مفتاح التشفير أو استخدام مفتاح افتراضي للأمان
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mahjoub_secret_key_2026')
    
    # جلب رابط قاعدة البيانات من بيئة Railway أو استخدام SQLite محلياً للتجربة
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # تصحيح الرابط إذا كان يبدأ بـ postgres:// ليصبح postgresql:// (مهم لـ SQLAlchemy)
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    
    # إذا لم يجد الرابط (في حال التشغيل المحلي)، يستخدم ملف sqlite
    if not SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///mahjoub_online.db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
