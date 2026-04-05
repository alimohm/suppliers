import string
import random
from database import db
from datetime import datetime

# دالة توليد رقم المحفظة الفريد (MAH-XXXXXXXX)
def generate_wallet_id():
    chars = string.ascii_uppercase + string.digits
    random_code = ''.join(random.choices(chars, k=8))
    return f"MAH-{random_code}"

# --- [ 1. جدول الإدارة العليا ] ---
class AdminUser(db.Model):
    __tablename__ = 'admin_user'
    id = db.Column(db.Integer, primary_key=True)
    # أندكس لسرعة تسجيل دخول الإدارة
    username = db.Column(db.String(100), unique=True, nullable=False, index=True) 
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default="Super Admin")

# --- [ 2. جدول الموردين ] ---
class Vendor(db.Model):
    __tablename__ = 'vendor' 
    id = db.Column(db.Integer, primary_key=True)
    
    # أندكس لأننا نبحث باليوزر في كل مرة يدخل فيها المورد
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=False)
    
    # أندكس لسرعة البحث عن البراند في محركات البحث الداخلية
    brand_name = db.Column(db.String(150), index=True)
    
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    
    # أندكس لسرعة ترتيب الموردين حسب تاريخ الانضمام (الأحدث أولاً)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    id_card_image = db.Column(db.String(500), nullable=True)
    commercial_registry_image = db.Column(db.String(500), nullable=True)

    # أندكس لسرعة فلترة الموردين (نشط / معلق) في لوحة التحكم
    status = db.Column(db.String(50), default="معلق", index=True)
    is_active = db.Column(db.Boolean, default=False, index=True) 
    
    staff = db.relationship('VendorStaff', back_populates='vendor', lazy=True)
    wallet = db.relationship('Wallet', backref='vendor_ref', uselist=False, cascade="all, delete-orphan")
    products = db.relationship('Product', backref='vendor_info', lazy=True)

# --- [ 3. جدول موظفي المورد ] ---
class VendorStaff(db.Model):
    __tablename__ = 'vendor_staff'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False, index=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=False)
    national_id = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True) 

    vendor = db.relationship('Vendor', back_populates='staff')

# --- [ 4. جدول المحفظة ] ---
class Wallet(db.Model):
    __tablename__ = 'wallet'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), unique=True, nullable=False, index=True)
    
    # الأندكس الأهم: كل عملية مالية ستبحث عن هذا الرقم
    wallet_number = db.Column(db.String(20), unique=True, default=generate_wallet_id, index=True)
    
    balance = db.Column(db.Float, default=0.0)
    pending_balance = db.Column(db.Float, default=0.0)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)

# --- [ 5. جدول المنتجات ] ---
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    
    # أندكس لسرعة البحث عن المنتجات بالاسم
    name = db.Column(db.String(150), nullable=False, index=True)
    brand = db.Column(db.String(100), index=True)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='YER')
    stock = db.Column(db.Integer, default=1)
    
    # أندكس لفلترة المنتجات حسب الحالة (مقبول/مرفوض/معلق)
    status = db.Column(db.String(20), default='pending', index=True) 
    
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<Product {self.name}>'

# --- [ 6. دالة حقن البيانات (Seed) ] ---
def seed_system():
    if not AdminUser.query.filter_by(username="علي").first():
        db.session.add(AdminUser(username="علي", password="123", role="Super Admin"))
    
    vendor_acc = Vendor.query.filter_by(username="علي محمد").first()
    if not vendor_acc:
        vendor_acc = Vendor(
            username="علي محمد", 
            password="123", 
            brand_name="محجوب أونلاين",
            phone="777777777",
            status="نشط",
            is_active=True
        )
        db.session.add(vendor_acc)
        db.session.commit() 

    if vendor_acc and not Wallet.query.filter_by(vendor_id=vendor_acc.id).first():
        new_wallet = Wallet(vendor_id=vendor_acc.id)
        db.session.add(new_wallet)

    db.session.commit()
