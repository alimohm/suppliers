import os
from flask_sqlalchemy import SQLAlchemy

# 1. تعريف الكائن أولاً لمنع التعليق
db = SQLAlchemy()

# 2. تعريف النموذج (Model) مباشرة داخل الملف
class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    owner_name = db.Column(db.String(120))
    brand_name = db.Column(db.String(120)) # أضفنا هذا للهيكل الجديد
    brand_logo_url = db.Column(db.String(255))

# 3. دالة التهيئة تأتي في النهاية
def init_db(app):
    uri = os.environ.get('DATABASE_URL')
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    
    app.config.update(
        SQLALCHEMY_DATABASE_URI=uri or 'sqlite:///local.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY=os.environ.get('SK', 'MAHJOUB_SECRET_2026')
    )
    db.init_app(app)
    with app.app_context():
        db.create_all()
