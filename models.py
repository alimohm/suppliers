from database import db
from datetime import datetime

# 1. جدول الموردين (الشركاء)
class Vendor(db.Model):
    __tablename__ = 'vendor'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    brand_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات السيادية
    wallet = db.relationship('Wallet', backref='vendor', uselist=False, cascade="all, delete-orphan")
    staff = db.relationship('VendorStaff', backref='vendor', lazy=True, cascade="all, delete-orphan")
    products = db.relationship('Product', backref='vendor', lazy=True)

# 2. جدول موظفي الموردين
class VendorStaff(db.Model):
    __tablename__ = 'vendor_staff'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), default='staff') # manager, staff
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)

# 3. جدول المحفظة المالية (نظام MAH)
class Wallet(db.Model):
    __tablename__ = 'wallet'
    id = db.Column(db.Integer, primary_key=True)
    wallet_number = db.Column(db.String(50), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default='YER') # أو SAR / USD
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    transactions = db.relationship('Transaction', backref='wallet', lazy=True)

# 4. جدول العمليات المالية (سجل الحركات)
class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20)) # 'deposit', 'withdrawal', 'sale'
    description = db.Column(db.String(200))
    status = db.Column(db.String(20), default='completed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'))

# 5. جدول المنتجات (المخزون)
class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(100))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))

# 6. جدول الإدارة العليا (علي محجوب)
class AdminUser(db.Model):
    __tablename__ = 'admin_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

def seed_initial_data():
    """تأمين دخول القائد علي محجوب"""
    admin = AdminUser.query.filter_by(username="علي محجوب").first()
    if not admin:
        new_admin = AdminUser(username="علي محجوب", password="123")
        db.session.add(new_admin)
        db.session.commit()
