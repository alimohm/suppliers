import os
from flask_sqlalchemy import SQLAlchemy

# 1. تعريف كائن قاعدة البيانات أولاً لمنع التعليق (Circular Import)
db = SQLAlchemy()

# 2. تعريف نموذج المورد (Vendor Model) متوافق مع قاعدة بياناتك
class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    owner_name = db.Column(db.String(120))
    # حقول الهوية البصرية والمالية
    brand_name = db.Column(db.String(120))
    brand_logo_url = db.Column(db.String(255))
    wallet_address = db.Column(db.String(255)) # متوافق مع الحقل الموجود في Postgres

# 3. دالة تهيئة قاعدة البيانات والربط مع Railway
def init_db(app):
    # جلب رابط قاعدة البيانات من متغيرات التطبيق في Railway
    uri = os.environ.get('DATABASE_URL')
    
    # تصحيح بروتوكول SQLAlchemy ليتوافق مع Postgres الحديثة
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    
    # إعدادات التهيئة
    app.config.update(
        SQLALCHEMY_DATABASE_URI=uri or 'sqlite:///local.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY=os.environ.get('SK', 'MAHJOUB_SECURE_2026')
    )
    
    db.init_app(app)
    
    # إنشاء الجداول تلقائياً في حال عدم وجودها
    with app.app_context():
        db.create_all()
