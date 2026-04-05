
from database import db
from datetime import datetime
import random

# 1. جدول الإدارة العليا (Admin)
class AdminUser(db.Model):
    __tablename__ = 'admin_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password = db.Column(db.String(128), nullable=False)

# 2. جدول الموردين (Vendors)
class Vendor(db.Model):
    __tablename__ = 'vendors'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    brand_name = db.Column(db.String(120), nullable=False, index=True)
    password = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20), index=True)
    
    # توثيق سيادي
    id_card_image = db.Column(db.String(255))
    status = db.Column(db.String(20), default="معلق", index=True)
    is_active = db.Column(db.Boolean, default=False, index=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # علاقات
    wallet = db.relationship('Wallet', backref='vendor', uselist=False, cascade="all, delete-orphan")
    products = db.relationship('Product', backref='vendor', lazy=True)
    staff = db.relationship('VendorStaff', backref='vendor', lazy=True)

# 3. جدول المحفظة المالية (Wallet)
class Wallet(db.Model):
    __tablename__ = 'wallets'
    id = db.Column(db.Integer, primary_key=True)
    wallet_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    balance = db.Column(db.Float, default=0.0)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False, index=True)

    def __init__(self, **kwargs):
        super(Wallet, self).__init__(**kwargs)
        if not self.wallet_number:
            self.wallet_number = f"MAH-{random.randint(1000000, 9999999)}"

# 4. جدول كشف الحساب (Transactions) - الحركة الكاملة
class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False, index=True)
    
    # تفاصيل الحركة
    trans_type = db.Column(db.String(50), nullable=False, index=True) # (إيداع، سحب، مبيع، عمولة)
    amount = db.Column(db.Float, nullable=False) # المبلغ المضاف أو المخصوم
    balance_after = db.Column(db.Float, nullable=False) # الرصيد الصافي بعد هذه الحركة
    description = db.Column(db.String(255)) # شرح (مثلاً: مبيع طلب رقم #55)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # ربط المحفظة بالعمليات
    wallet = db.relationship('Wallet', backref=db.backref('transactions', lazy='dynamic'))

# 5. جدول طاقم العمل (Vendor Staff)
class VendorStaff(db.Model):
    __tablename__ = 'vendor_staff'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password = db.Column(db.String(128), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False, index=True)

# 6. جدول المنتجات (Products)
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50), index=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False, index=True)
