from datetime import datetime
from database import db

# ==========================================
# 1. الإدارة العليا (علي محجوب)
# ==========================================
class SuperAdmin(db.Model):
    __tablename__ = 'super_admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), default='علي محجوب')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==========================================
# 2. فريق عمل الإدارة
# ==========================================
class AdminStaff(db.Model):
    __tablename__ = 'admin_staff'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='مراقب نظام')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==========================================
# 3. الموردين (أصحاب المتاجر)
# ==========================================
class Vendor(db.Model):
    __tablename__ = 'vendor'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    brand_name = db.Column(db.String(100), index=True)
    phone = db.Column(db.String(20))
    status = db.Column(db.String(50), default='قيد الانتظار')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # علاقات الربط
    wallet = db.relationship('Wallet', backref='owner', uselist=False, cascade="all, delete-orphan")
    products = db.relationship('Product', backref='supplier', lazy=True)

# ==========================================
# 4. موظفي الموردين (Vendor Staff)
# ==========================================
class VendorStaff(db.Model):
    __tablename__ = 'vendor_staff'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==========================================
# 5. المنتجات (Products)
# ==========================================
class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, default=0.0)
    stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==========================================
# 6. المحفظة (Wallet MAH)
# ==========================================
class Wallet(db.Model):
    __tablename__ = 'wallet'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), unique=True)
    wallet_number = db.Column(db.String(50), unique=True, nullable=False)
    balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==========================================
# 7. المعاملات (Transactions)
# ==========================================
class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'))
    tx_type = db.Column(db.String(50)) # ايداع، سحب، نظام
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def seed_initial_data():
    if not SuperAdmin.query.filter_by(username='علي محجوب').first():
        admin = SuperAdmin(username='علي محجوب', password='ali_password_2026')
        db.session.add(admin)
        db.session.commit()
