from flask import session
from werkzeug.security import check_password_hash
from models import Vendor, VendorStaff, db

def login_vendor(u, p):
    """التحقق من دخول (محجوب أونلاين) أو موظفيه بالاسم العربي"""
    if not u or not p:
        return False, "يرجى إدخال اسم المستخدم العربي وكلمة المرور."

    clean_username = u.strip()

    # 1. البحث أولاً في جدول الملاك (Owners)
    vendor = Vendor.query.filter_by(username=clean_username).first()
    if vendor:
        # ملاحظة: في التجريب نستخدم التحقق المباشر، في الإنتاج نستخدم check_password_hash
        if vendor.password == p or check_password_hash(vendor.password, p):
            if vendor.status == "محظور":
                return False, "عذراً، هذا الحساب محظور حالياً. يرجى التواصل مع علي محجوب."
            
            session.clear()
            session['user_id'] = vendor.id
            session['role'] = 'vendor_owner' # تحديد أنه المالك (يرى المحفظة)
            session['username'] = vendor.username
            session['brand'] = vendor.brand_name
            return True, f"مرحباً بك يا سيد {vendor.username} في لوحة تحكم {vendor.brand_name}."

    # 2. إذا لم يكن مالكاً، نبحث في جدول الموظفين (Staff)
    staff = VendorStaff.query.filter_by(username=clean_username).first()
    if staff:
        if staff.password == p or check_password_hash(staff.password, p):
            # التأكد من حالة المورد الأصلي (إذا كان المالك محظوراً، الموظف لا يدخل)
            if staff.owner.status == "محظور":
                return False, "الحساب الرئيسي لهذه العلامة التجارية موقوف."

            session.clear()
            session['user_id'] = staff.vendor_id # ربطه بالـ ID الخاص بالمالك للعمليات
            session['staff_id'] = staff.id
            session['role'] = 'vendor_staff' # تحديد أنه موظف (المحفظة محجوبة عنه)
            session['username'] = staff.username
            session['brand'] = staff.owner.brand_name
            return True, f"تم دخول الموظف {staff.username} بنجاح."

    return False, "هذا الاسم العربي غير مسجل أو البيانات غير صحيحة."

def is_logged_in():
    """التحقق من وجود جلسة نشطة للمورد أو موظفه"""
    return session.get('role') in ['vendor_owner', 'vendor_staff']

def can_see_wallet():
    """المنطق الذهبي: هل يرى المستخدم المحفظة؟"""
    return session.get('role') == 'vendor_owner'
