import os
from flask_sqlalchemy import SQLAlchemy

# 1. تعريف كائن قاعدة البيانات
db = SQLAlchemy()

# 2. تعريف نموذج المورد بالهيكل الملكي الكامل
class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    owner_name = db.Column(db.String(120))
    brand_name = db.Column(db.String(120))
    brand_logo_url = db.Column(db.String(255))
    wallet_address = db.Column(db.String(255))

# 3. دالة التهيئة والإصلاح التلقائي
def init_db(app):
    # جلب الرابط من متغيرات نظام Railway
    uri = os.environ.get('DATABASE_URL')
    
    # تصحيح البروتوكول ليتوافق مع Postgres
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    
    app.config.update(
        SQLALCHEMY_DATABASE_URI=uri or 'sqlite:///local.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY=os.environ.get('SK', 'MAHJOUB_SECURE_2026')
    )
    
    db.init_app(app)
    
    with app.app_context():
        # إعادة بناء الجدول لحل مشكلة الأعمدة المفقودة
        db.drop_all() 
        db.create_all()
        
        # إنشاء حساب 'ali' تلقائياً لضمان الدخول الفوري
        if not Vendor.query.filter_by(username='ali').first():
            new_v = Vendor(
                username='ali',
                password='123',
                owner_name='علي محجوب',
                brand_name='محجوب أونلاين',
                wallet_address='MQ-5035D99C'
            )
            db.session.add(new_v)
            db.session.commit()
