import random
import string
from datetime import datetime
from werkzeug.security import generate_password_hash
from database import db 

def generate_mah_wallet():
    """توليد عنوان محفظة فريد للمنصة"""
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"MAH-{suffix}"

# --- النماذج (Models) ---

class Vendor(db.Model):
    __tablename__ = 'vendor'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False) 
    employee_name = db.Column(db.String(120)) 
    brand_name = db.Column(db.String(120), nullable=False)    
    phone_number = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True) 
    status = db.Column(db.String(30), default='active') 
    wallet_address = db.Column(db.String(255), unique=True, default=generate_mah_wallet)
    products = db.relationship('Product', backref='vendor_owner', lazy=True)

class AdminUser(db.Model):
    __tablename__ = 'admin_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- دالة حقن البيانات (Seed Function) ---

def seed_admin():
    """إنشاء الحسابات الافتراضية للنظام"""
    try:
        # كلمة مرور افتراضية (يفضل تغييرها لاحقاً)
        secure_pw = generate_password_hash('123')
        
        # 1. إنشاء حساب الإدارة المركزية (علي محجوب)
        admin_name = "علي محجوب"
        if not AdminUser.query.filter_by(username=admin_name).first():
            new_admin = AdminUser(
                username=admin_name, 
                password=secure_pw
            )
            db.session.add(new_admin)
            print(f"✅ تم بنجاح إنشاء المسؤول: {admin_name}")
        
        # 2. إنشاء حساب المورد الرسمي (محجوب أونلاين)
        vendor_name = "محجوب أونلاين"
        if not Vendor.query.filter_by(username=vendor_name).first():
            new_vendor = Vendor(
                username=vendor_name, 
                password=secure_pw, 
                brand_name='Mahjoub Online',
                employee_name='إدارة محجوب',
                status='active'
            )
            db.session.add(new_vendor)
            print(f"✅ تم بنجاح إنشاء المورد الرسمي: {vendor_name}")
            
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"⚠️ خطأ أثناء تحديث البيانات: {e}")
