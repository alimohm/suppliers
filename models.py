import random
import string
from datetime import datetime
from database import db

def generate_mah_wallet():
    """توليد عنوان محفظة فريد يبدأ بـ MAH متبوع بـ 10 رموز"""
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"MAH-{suffix}"

class Vendor(db.Model):
    """جدول الموردين والموظفين - الكيان اللامركزي لمحجوب أونلاين"""
    __tablename__ = 'vendor'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # بيانات الدخول للموظف (مثلاً: username: moshtaq)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    
    # الحقول التشغيلية
    employee_name = db.Column(db.String(120), nullable=True) 
    brand_name = db.Column(db.String(120), nullable=False)    
    
    # --- إضافة للمدير (علي) ---
    is_active = db.Column(db.Boolean, default=True) # يسمح لك بتعطيل المورد
    
    # الهوية الرقمية اللامركزية للمؤسسة
    wallet_address = db.Column(db.String(255), unique=True, default=generate_mah_wallet)
    
    # توكن الربط الخارجي
    qomra_access_token = db.Column(db.Text, nullable=True)
    
    # علاقة المنتجات
    products = db.relationship('Product', backref='vendor_owner', lazy=True)

    def __repr__(self):
        return f'<Vendor Employee: {self.employee_name} | Brand: {self.brand_name}>'

class Product(db.Model):
    """جدول المنتجات - قلب منصة محجوب أونلاين اللامركزية"""
    __tablename__ = 'product'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    brand = db.Column(db.String(120), nullable=True)  
    
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='YER') 
    stock = db.Column(db.Integer, default=1)           
    
    # المحتوى والوسائط (تم تعديل image_file ليدعم ميديا متعددة)
    description = db.Column(db.Text)
    image_file = db.Column(db.Text) # نص طويل يخزن مسارات الصور والفيديو مفصولة بفاصلة
    
    # --- حقول التحكم الإداري (علي) ---
    # الحالة: pending (انتظار)، approved (مقبول)، rejected (مرفوض)
    status = db.Column(db.String(20), default='pending') 
    is_published = db.Column(db.Boolean, default=False)
    
    # الربط التقني
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id')) 
    vendor_username = db.Column(db.String(80))                    
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # تاريخ الإضافة

    def __repr__(self):
        return f'<Product {self.name} - Status: {self.status}>'

# --- جدول اختياري للمدير العام (علي) لزيادة الأمان ---
class AdminUser(db.Model):
    __tablename__ = 'admin_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
