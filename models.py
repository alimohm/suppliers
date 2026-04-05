from database import db
from datetime import datetime

# 1. مودل الموردين
class Vendor(db.Model):
    __tablename__ = 'vendor' # تأكيد اسم الجدول لقاعدة بيانات Postgres
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    brand_name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=False)
    
    # العلاقات
    wallet = db.relationship('Wallet', backref='vendor', uselist=False, cascade="all, delete-orphan")
    staff = db.relationship('VendorStaff', backref='vendor', lazy=True, cascade="all, delete-orphan")

# 2. مودل الموظفين (الذي كان يسبب الانهيار)
class VendorStaff(db.Model):
    __tablename__ = 'vendor_staff'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)

# 3. مودل المحفظة (الرابط المالي)
class Wallet(db.Model):
    __tablename__ = 'wallet'
    id = db.Column(db.Integer, primary_key=True)
    wallet_number = db.Column(db.String(50), unique=True)
    balance = db.Column(db.Float, default=0.0)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))

# 4. مودل المدير (علي محجوب)
class AdminUser(db.Model):
    __tablename__ = 'admin_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

def seed_initial_data():
    """زرع بيانات المالك علي محجوب"""
    # البحث عنك في قاعدة بيانات Postgres
    admin = AdminUser.query.filter_by(username="علي محجوب").first()
    if not admin:
        new_admin = AdminUser(username="علي محجوب", password="123")
        db.session.add(new_admin)
        try:
            db.session.commit()
            print("✅ تم زرع حساب علي محجوب في Postgres")
        except Exception as e:
            db.session.rollback()
            print(f"❌ فشل الزرع: {e}")
