import os
from flask import session, request
from models import AdminUser, Vendor, Wallet, VendorStaff, db
from werkzeug.utils import secure_filename

# 1. تحقق دخول المؤسس (علي محجوب)
def verify_admin_credentials(u, p):
    clean_username = u.strip() if u else ""
    # البحث في الإنديكس عن المؤسس
    admin = AdminUser.query.filter_by(username=clean_username).first()
    if admin and admin.password == p:
        session.clear()
        session['user_id'] = admin.id
        session['username'] = admin.username
        session['role'] = 'super_admin'
        return True, f"أهلاً بك يا قائد المسيرة، {admin.username}"
    return False, "بيانات دخول المؤسس غير صحيحة."

# 2. تحقق دخول المورد (صاحب المتجر)
def verify_vendor_credentials(u, p):
    clean_username = u.strip() if u else ""
    # البحث في الإنديكس عن المورد
    vendor = Vendor.query.filter_by(username=clean_username).first()
    if vendor and vendor.password == p:
        if not vendor.is_active:
            return False, "الحساب بانتظار التفعيل السيادي."
        session.clear()
        session['user_id'] = vendor.id
        session['brand_name'] = vendor.brand_name
        session['role'] = 'vendor'
        return True, f"مرحباً بك في متجرك، {vendor.brand_name}"
    return False, "بيانات دخول المورد غير صحيحة."

# 3. تحقق دخول الموظف (طاقم العمل)
def verify_staff_credentials(u, p):
    clean_username = u.strip() if u else ""
    # البحث في الإنديكس عن الموظف
    staff = VendorStaff.query.filter_by(username=clean_username).first()
    if staff and staff.password == p:
        session.clear()
        session['user_id'] = staff.id
        session['username'] = staff.username
        session['vendor_id'] = staff.vendor_id
        session['role'] = 'staff'
        return True, f"مرحباً بك يا {staff.username} في طاقم العمل."
    return False, "بيانات دخول الموظف غير صحيحة."

# دالة جلب الموردين لبرج المراقبة (المطلوبة في app.py)
def manage_accounts_logic():
    return Vendor.query.order_by(Vendor.id.desc()).all()

# دالة الإحصائيات السريعة
def get_admin_stats():
    try:
        return {
            'total_vendors': Vendor.query.count(),
            'active_wallets': Wallet.query.count()
        }
    except:
        return {'total_vendors': 0, 'active_wallets': 0}

# دالة إنشاء مورد جديد من لوحة الآدمن
def create_vendor_logic():
    if request.method == 'POST':
        u = request.form.get('username')
        bn = request.form.get('brand_name')
        p = request.form.get('password')
        if not u or not p: return False, "بيانات ناقصة."
        
        if Vendor.query.filter_by(username=u).first():
            return False, "اسم المستخدم محجوز."
            
        new_v = Vendor(username=u, brand_name=bn, password=p, is_active=True, status="نشط")
        db.session.add(new_v)
        db.session.flush()
        db.session.add(Wallet(vendor_id=new_v.id))
        db.session.commit()
        return True, f"تم إنشاء المورد {bn} ومحفظته بنجاح."
    return False, "طلب غير صالح."
