import os
from flask_sqlalchemy import SQLAlchemy

# 1. تعريف كائن قاعدة البيانات أولاً لمنع التعليق
db = SQLAlchemy()

# 2. تعريف نموذج المورد (Vendor Model)
class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    owner_name = db.Column(db.String(120))
    # حقول إضافية لدعم الهوية البصرية للمورد
    brand_name = db.Column(db.String(120))
    brand_logo_url = db.Column(db.String(255))

# 3. دالة تهيئة قاعدة البيانات والربط مع Railway
def init_db(app):
    # جلب رابط قاعدة البيانات من متغيرات النظام في Railway
    uri = os.environ.get('DATABASE_URL')
    
    # تصحيح بروتوكول SQLAlchemy ليتوافق مع Postgres الحديثة
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    
    app.config.update(
        SQLALCHEMY_DATABASE_URI=uri or 'sqlite:///local.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY=os.environ.get('SK', 'MAHJOUB_SECURE_KEY_2026')
    )
    
    db.init_app(app)
    
    # إنشاء الجداول تلقائياً عند التشغيل
    with app.app_context():
        db.create_all()
