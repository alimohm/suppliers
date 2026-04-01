import os

class Config:
    # الهوية الرقمية للمنصة
    PLATFORM_NAME = "محجوب أونلاين"
    SLOGAN = "سوقك الذكي"
    
    # المفاتيح والأمان
    SECRET_KEY = os.environ.get('SK', 'MAHJOUB_ROYAL_2026_PRIVATE_KEY')
    
    # الربط مع قاعدة البيانات (Postgres في Railway)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
