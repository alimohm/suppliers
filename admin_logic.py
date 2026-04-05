from flask import session, request, redirect, url_for
from models import AdminUser, Vendor, Wallet, db

def verify_admin_credentials(u, p):
    """
    تحقق منطقي ذكي لدخول المسؤول
    """
    clean_username = u.strip() if u else ""
    
    if not clean_username or not p:
        return False, "يرجى إدخال بيانات الدخول كاملة."

    admin = AdminUser.query.filter_by(username=clean_username).first()
    
    if not admin:
        return False, "هذا الاسم غير مسجل في المنصة اللامركزية."

    if admin.password != p:
        return False, "كلمة المرور غير صحيحة، يرجى المحاولة مرة أخرى."

    session.clear()
    session['admin_id'] = admin.id
    session['role'] = 'super_admin'
    session['username'] = admin.username
    
    return True, "تم التحقق بنجاح. مرحباً بك في مركز القيادة."

def manage_accounts_logic():
    """
    جلب كافة الموردين لعرضهم في لوحة الاعتماد
    """
    vendors = Vendor.query.order_by(Vendor.id.desc()).all()
    return vendors

def create_vendor_logic():
    """
    المنطق السيادي لإنشاء مورد وتفعيل محفظته تلقائياً
    """
    if request.method == 'POST':
        username = request.form.get('username')
        brand_name = request.form.get('brand_name')
        password = request.form.get('password')

        # فحص التكرار لضمان فرادة الحساب
        if Vendor.query.filter_by(username=username).first():
            return False, "اسم المستخدم هذا محجوز مسبقاً."

        # 1. إنشاء سجل المورد
        new_vendor = Vendor(
            username=username,
            brand_name=brand_name,
            password=password, 
            status="نشط",
            is_active=True
        )
        
        try:
            db.session.add(new_vendor)
            db.session.flush() # الحصول على ID قبل الحفظ النهائي

            # 2. توليد المحفظة السيادية تلقائياً (MAH-XXXX)
            new_wallet = Wallet(vendor_id=new_vendor.id)
            db.session.add(new_wallet)
            
            db.session.commit()
            return True, f"تم اعتماد {brand_name} وتفعيل السيادة المالية."
            
        except Exception as e:
            db.session.rollback()
            return False, f"حدث خطأ فني: {str(e)}"

    return False, "طلب غير صالح."
