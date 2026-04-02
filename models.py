import random
import string
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
    
    # الحقول التشغيلية (الربط بين الموظف والمؤسسة)
    employee_name = db.Column(db.String(120), nullable=True) # الاسم: مشتاق الفقيه
    brand_name = db.Column(db.String(120), nullable=False)    # المؤسسة: عمار الفقيه للتجارة
    
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
    
    # براند المنتج (يُملأ آلياً بـ "عمار الفقيه للتجارة" عند الإضافة)
    brand = db.Column(db.String(120), nullable=True)  
    
    # التفاصيل المالية والمخزون
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='YER') # (YER, SAR, USD)
    stock = db.Column(db.Integer, default=1)           # الكمية المتوفرة
    
    # المحتوى والوسائط
    description = db.Column(db.Text)
    image_file = db.Column(db.String(200))
    is_published = db.Column(db.Boolean, default=False)
    
    # الربط التقني (تتبع الموظف والمؤسسة)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id')) # ربط بـ ID الموظف
    vendor_username = db.Column(db.String(80))                    # يوزر الموظف (للتدقيق)

    def __repr__(self):
        return f'<Product {self.name} - Added by {self.vendor_username}>'
