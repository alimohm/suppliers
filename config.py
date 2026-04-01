import os

class Config:
    # جلب رابط قاعدة البيانات من Railway أو استخدام sqlite للتجربة المحلية
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'MAHJOUB_2026_ROYAL')
    
    # الثوابت المالية السيادية
    PLATFORM_FEE_PERCENT = 30.0  # نسبة الـ 30%
    CURRENCY_DEFAULT = "MQ"      # عملة المحفظة السيادية
