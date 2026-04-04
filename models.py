from database import db
from datetime import datetime
from werkzeug.security import generate_password_hash

# --- [ 1. جدول الإدارة العليا: علي محجوب ] ---
class AdminUser(db.Model):
    __tablename__ = 'admin_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default="Super Admin") # العمود الذي كان مفقوداً

# --- [ 2. جدول الموردين: الملاك ] ---
class Vendor(db.Model):
    __tablename__ = 'vendor'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    brand_name = db.Column(db.String(150))
    employee_name = db.Column(db.String(150))
    phone_number = db.Column(db.String(20))
    status = db.Column(db.String(50), default="نشط") # العمود الذي كان مفقوداً
    wallet_address = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    
    # علاقة لربط الموظفين بالمورد
    staff = db.relationship('VendorStaff', backref='owner', lazy=True)

# --- [ 3. جدول موظفي المورد ] ---
class VendorStaff(db.Model):
    __tablename__ = 'vendor_staff'
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    national_id = db.Column(db.String(100), nullable=False)

# --- [ دالة حقن البيانات السيادية ] ---
def seed_system():
    try:
        # حقن حساب الإدارة: علي محجوب
        admin = AdminUser.query.filter_by(username="علي محجوب").first()
        if not admin:
            new_admin = AdminUser(
                username="علي محجوب", 
                password="admin_password_123", 
                role="Super Admin"
            )
            db.session.add(new_admin)
        
        # حقن حساب المورد الرئيسي: محجوب أونلاين
        vendor = Vendor.query.filter_by(username="ali_mahjoub").first()
        if not vendor:
            new_vendor = Vendor(
                username="ali_mahjoub", 
                password="vendor_password_123",
                brand_name="محجوب أونلاين",
                status="نشط"
            )
            db.session.add(new_vendor)
            
        db.session.commit()
        print("✨ تم فحص وحقن البيانات السيادية بنجاح.")
    except Exception as e:
        db.session.rollback()
        print(f"❌ خطأ أثناء حقن البيانات: {e}")
