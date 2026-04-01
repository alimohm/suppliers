import os
import random
import string
from flask_sqlalchemy import SQLAlchemy

# 1. تعريف كائن قاعدة البيانات
db = SQLAlchemy()

# 2. نموذج المورد مع الحقول الجديدة (الهاتف، البراند، المحفظة)
class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    owner_name = db.Column(db.String(120))
    brand_name = db.Column(db.String(120))
    brand_logo_url = db.Column(db.String(255))
    wallet_address = db.Column(db.String(255), unique=True) # محفظة MAH الفريدة

def generate_mah_wallet():
    """توليد رقم محفظة يبدأ بـ MAH متبوعاً بـ 8 رموز عشوائية"""
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(random.choice(chars) for _ in range(8))
    return f"MAH-{suffix}"

def init_db(app):
    # جلب الرابط من Railway
    uri = os.environ.get('DATABASE_URL')
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    
    app.config.update(
        SQLALCHEMY_DATABASE_URI=uri or 'sqlite:///local.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY=os.environ.get('SK', 'MAHJOUB_2026')
    )
    
    db.init_app(app)
    
    with app.app_context():
        # إعادة بناء الجداول لضمان وجود الحقول الجديدة
        db.drop_all() 
        db.create_all()
        
        # إنشاء حسابك 'ali' ببياناته التلقائية
        if not Vendor.query.filter_by(username='ali').first():
            new_v = Vendor(
                username='ali',
                password='123',
                phone='77xxxxxxx',
                owner_name='علي محجوب',
                brand_name='محجوب أونلاين', # الاسم الرسمي للمنصة
                wallet_address=generate_mah_wallet() # توليد MAH تلقائي
            )
            db.session.add(new_v)
            db.session.commit()
