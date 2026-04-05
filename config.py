import os

class Config:
    # مفتاح الأمان لتشفير الجلسات (Sessions) وحماية البيانات
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'MAHJOUB_SUPER_2026_KEY'
    
    # ربط النظام بقاعدة بيانات SQLite (ستنشأ تلقائياً باسم mahjoub_database.db)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///mahjoub_database.db'
    
    # تحسين الأداء عبر إيقاف تنبيهات التعديل غير الضرورية
    SQLALCHEMY_TRACK_MODIFICATIONS = False
