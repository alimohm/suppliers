
from database import db
from datetime import datetime
import random

# ==========================================
# 1. جدول الإدارة العليا (Admin/Owner)
# ==========================================
class AdminUser(db.Model):
    __tablename__ = 'admin_users'
    id = db.Column(db.Integer, primary_key=True)
    # username مؤندكس لضمان تسجيل دخول لحظي للمالك
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password = db.Column(db.String(128), nullable=False)

# ==========================================
# 2. جدول الموردين (Vendors) - المحرك التجاري
# ==========================================
class Vendor(db.Model):
    __tablename__ = 'vendors'
    id = db.Column(db.Integer, primary_key=True)
    # اليوزرنيم والبراند مؤندكسين لسرعة البحث والتحقق
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    brand_name = db.Column(db.String(120), nullable=False, index=True)
    password = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20), index=True)
    
    # صور التوثيق السيادي
    id_card_image = db.Column(db.String(255), nullable=True)
    commercial_registry_image = db.Column(db.String(255), nullable=True)
    
    # الحالة والتحكم (مؤندكس للفلترة في برج المراقبة)
    status = db.Column(db.String(20), default="معلق", index=True) 
    is_active = db.Column(db.Boolean, default=False, index=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # العلاقات (Relationships)
    # علاقة 1 لـ 1 مع المحفظة (uselist=False)
    wallet = db.relationship('Wallet', backref='vendor', uselist=False, cascade="all, delete-orphan")
    # علاقة 1 لـ N مع المنتجات والموظفين
    products = db.relationship('Product', backref='vendor', lazy=True)
    staff = db.relationship('VendorStaff', backref='vendor', lazy=True)

# ==========================================
# 3. جدول المحفظة المالية (Wallet) - النظام المالي MAH
# ==========================================
class Wallet(db.Model):
    __tablename__ = 'wallets'
    id = db.Column(db.Integer, primary_key=True)
    # رقم المحفظة مؤندكس سيادياً للعمليات المالية السريعة
    wallet_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    balance = db.Column(db.Float, default=0.0)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False, index=True)

    def __init__(self, **kwargs):
        super(Wallet, self).__init__(**kwargs)
        # توليد رقم محفظة تلقائي يبدأ بـ MAH عند الإنشاء
        if not self.wallet_number:
            self.wallet_number = f"MAH-{random.randint(1000000, 9999999)}"

# ==========================================
# 4. جدول طاقم عمل المورد (Vendor Staff)
# ==========================================
class VendorStaff(db.Model):
    __tablename__ = 'vendor_staff'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default="staff", index=True) 
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False, index=True)

# ==========================================
# 5. جدول المنتجات (Products) - مخزن البيانات
# ==========================================
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    # اسم المنتج والقسم مؤندكسين لسرعة تصفح الزبائن
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(255))
    category = db.Column(db.String(50), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False, index=True)

# ==========================================
# دالة التأسيس التلقائي (Seed Data)
# ==========================================
def seed_initial_data():
    """زرع الحسابات الأولية في قاعدة البيانات"""
    # 1. إضافة المؤسس (علي محجوب)
    if not AdminUser.query.filter_by(username="ali_mahjoub").first():
        db.session.add(AdminUser(username="ali_mahjoub", password="123"))
        print("✅ تم زرع حساب المؤسس.")

    db.session.commit()
