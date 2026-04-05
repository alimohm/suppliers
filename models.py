from datetime import datetime
from database import db

# ==========================================
# 1. جدول الإدارة العليا (السيادة المطلقة)
# ==========================================
class SuperAdmin(db.Model):
    __tablename__ = 'super_admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), default='علي محجوب')
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # تاريخ التأسيس

# ==========================================
# 2. جدول الموردين (الشركاء التجاريين)
# ==========================================
class Vendor(db.Model):
    __tablename__ = 'vendor'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    
    # بيانات الهوية
    brand_name = db.Column(db.String(100), index=True) 
    phone = db.Column(db.String(20))
    
    # نظام الحالات وتاريخ الانضمام التلقائي
    status = db.Column(db.String(50), default='نشط') 
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True) # تاريخ الانضمام

    # الربط المباشر مع المحفظة (One-to-One)
    # عند حذف المورد، تُحذف محفظته تلقائياً لضمان نظافة البيانات
    wallet = db.relationship('Wallet', backref='owner_vendor', uselist=False, cascade="all, delete-orphan")

# ==========================================
# 3. جدول المحفظة (السيادة المالية MAH)
# ==========================================
class Wallet(db.Model):
    __tablename__ = 'wallet'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), unique=True)
    wallet_number = db.Column(db.String(50), unique=True, nullable=False, index=True) # تبدأ بـ MAH
    balance = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # تاريخ تدشين المحفظة

# ==========================================
# 4. جدول كشف الحساب (تتبع كل فلس)
# ==========================================
class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), index=True)
    
    tx_type = db.Column(db.String(20)) # مبيعات، سحب، إيداع
    amount = db.Column(db.Float, nullable=False)
    details = db.Column(db.String(255)) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

def seed_initial_data():
    """زرع بيانات علي محجوب كمسؤول نظام عند أول تشغيل"""
    admin_exists = SuperAdmin.query.filter_by(username='علي محجوب').first()
    if not admin_exists:
        new_admin = SuperAdmin(
            username='علي محجوب',
            password='ali_password_2026', # يجب تغييرها وتشفيرها لاحقاً
            full_name='علي محجوب'
        )
        db.session.add(new_admin)
        db.session.commit()
        print("✅ تم زرع بيانات الإدارة العليا بنجاح.")
