import random
import string
from database import db

def generate_mah_wallet():
    """توليد عنوان محفظة فريد يبدأ بـ MAH متبوع بـ 10 رموز"""
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    return f"MAH-{suffix}"

class Vendor(db.Model):
    """جدول الموردين - يمثل الكيان اللامركزي للتاجر"""
    __tablename__ = 'vendor'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False) # مثل: moshtaq
    password = db.Column(db.String(120), nullable=False)
    
    # العلامة التجارية (مثل: عمار الفقيه للتجارة)
    brand_name = db.Column(db.String(120), nullable=False)
    
    # المحفظة الرقمية اللامركزية
    wallet_address = db.Column(db.String(255), unique=True, default=generate_mah_wallet)
    
    qomra_access_token = db.Column(db.Text, nullable=True)
    products = db.relationship('Product', backref='vendor_owner', lazy=True)

    def __repr__(self):
        return f'<Vendor {self.brand_name} (@{self.username})>'

class Product(db.Model):
    """جدول المنتجات - قلب منصة محجوب أونلاين اللامركزية"""
    __tablename__ = 'product'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    brand = db.Column(db.String(120), nullable=True)  # براند المنتج نفسه
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='YER') # (YER, SAR, USD)
    stock = db.Column(db.Integer, default=1)           # الكمية المتوفرة
    description = db.Column(db.Text)
    image_file = db.Column(db.String(200))
    is_published = db.Column(db.Boolean, default=False)
    
    # الربط مع المورد (ForeignKey)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    vendor_username = db.Column(db.String(80))

    def __repr__(self):
        return f'<Product {self.name} - {self.price} {self.currency}>'
