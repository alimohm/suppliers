from database import db
from datetime import datetime

# --- [ جدول الإدارة العليا: علي محجوب ] ---
class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default="Super Admin")

# --- [ جدول الموردين: محجوب أونلاين ] ---
class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    brand_name = db.Column(db.String(150))
    employee_name = db.Column(db.String(150)) # اسم الموظف المسؤول
    phone_number = db.Column(db.String(20))
    status = db.Column(db.String(50), default="نشط") # الحقل الذي كان يسبب الخطأ
    wallet_address = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)

# --- [ دالة حقن البيانات السيادية ] ---
def seed_system():
    # إضافة علي محجوب كمدير عام
    if not AdminUser.query.filter_by(username="علي محجوب").first():
        db.session.add(AdminUser(username="علي محجوب", password="admin_password_123"))
    
    # إضافة مورد تجريبي
    if not Vendor.query.filter_by(username="ali_mahjoub").first():
        db.session.add(Vendor(
            username="ali_mahjoub", 
            password="vendor_password_123",
            brand_name="محجوب أونلاين",
            status="نشط"
        ))
    db.session.commit()
