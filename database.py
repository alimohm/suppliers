from flask_sqlalchemy import SQLAlchemy

# إنشاء كائن قاعدة البيانات السيادي
db = SQLAlchemy()

def init_db(app):
    """ربط قاعدة البيانات بالتطبيق وتفعيل المحرك"""
    db.init_app(app)
