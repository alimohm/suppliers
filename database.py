from flask_sqlalchemy import SQLAlchemy

# 1. إنشاء كائن قاعدة البيانات ككائن عالمي (Global Object)
db = SQLAlchemy()

def init_db(app):
    """
    2. ربط قاعدة البيانات بتطبيق Flask الرئيسي عند الإقلاع.
    هذه الدالة تُستدعى مرة واحدة فقط في ملف app.py.
    """
    db.init_app(app)
