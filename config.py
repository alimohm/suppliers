import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mahjoub_secret_key_2026')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # تصحيح رابط قاعدة البيانات ليتوافق مع SQLAlchemy
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    
    if not SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///mahjoub_online.db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
