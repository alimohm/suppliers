from datetime import datetime
from database import db

# ==========================================
# 1. جدول الإدارة العليا (السيادة المطلقة)
# ==========================================
class SuperAdmin(db.Model):
    __tablename__ = 'super_admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True) # indexed
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), default='علي محجوب')

# ==========================================
# 2. جدول موظفي الإدارة (فريق العمل الإداري)
# ==========================================
class AdminStaff(db.Model):
    __tablename__ = 'admin_staff'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='مراقب نظام') # مراقب مالي، دعم فني
    is_active = db.Column(db.Boolean, default=True)
    # صلاحيات دقيقة
    can_approve = db.Column(db.Boolean, default=False)
    can_block = db.Column(db.Boolean, default=False)

# ==========================================
# 3. جدول الموردين (الشركاء التجاريين)
# ==========================================
class Vendor(db.Model):
    __tablename__ = 'vendor'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    
    # بيانات الهوية الرسمية
    brand_name = db.Column(db.String(100), index=True) # اسم العلامة التجارية
    official_id = db.Column(db.String(100), unique=True) # السجل الرسمي
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    
    # نظام الحالات المنطقية
    status = db.Column(db.String(50), default='قيد الانتظار') # نشط، محظور، مرفوض، مقيد
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # العلاقات (Relations)
    wallet = db.relationship('Wallet', backref='owner_vendor', uselist=False)
    products = db.relationship('Product', backref='provider', lazy='dynamic')
    staff = db.relationship('VendorStaff', backref='employer', lazy='dynamic')

# ==========================================
# 4. جدول موظفي المورد (القوة التشغيلية للمتجر)
# ==========================================
class VendorStaff(db.Model):
    __tablename__ = 'vendor_staff'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), index=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='كاشير') # كاشير، مدير مخزن

# ==========================================
# 5. جدول المنتجات (المرتبط بالعلامة التجارية)
# ==========================================
class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False, index=True)
    
    name = db.Column(db.String(150), nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==========================================
# 6. جدول المحفظة (السيادة المالية MAH)
# ==========================================
class Wallet(db.Model):
    __tablename__ = 'wallet'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), unique=True)
    wallet_number = db.Column(db.String(50), unique=True, nullable=False, index=True) # تبدأ بـ MAH
    balance = db.Column(db.Float, default=0.0)
    
    transactions = db.relationship('Transaction', backref='parent_wallet', lazy='dynamic')

# ==========================================
# 7. جدول كشف الحساب (تتبع كل فلس)
# ==========================================
class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), index=True)
    
    tx_type = db.Column(db.String(20)) # مبيعات، سحب، إيداع، عمولة
    amount = db.Column(db.Float, nullable=False)
    prev_balance = db.Column(db.Float)
    new_balance = db.Column(db.Float)
    details = db.Column(db.String(255)) # مثلاً: "بيع منتج: آيفون 15"
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
