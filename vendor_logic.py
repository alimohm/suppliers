from flask import session
from models import Vendor, VendorStaff

def login_vendor(u, p):
    """
    تحقق منطقي ذكي للموردين والموظفين:
    1. التأكد من وجود الحساب أولاً.
    2. التأكد من مطابقة كلمة المرور.
    3. رسائل خطأ مخصصة للهوية اللامركزية.
    """
    
    # تنظيف المدخلات (username & password)
    username = u.strip() if u else ""
    password = p.strip() if p else ""

    if not username or not password:
        return False, "يرجى إدخال بيانات الدخول للمنصة."

    # --- [ الخطوة 1: فحص حسابات الملاك (Owners) ] ---
    vendor = Vendor.query.filter_by(username=username).first()
    
    if vendor:
        # الحساب موجود، الآن نفحص كلمة المرور
        if vendor.password == password:
            session.clear()
            session['user_id'] = vendor.id
            session['role'] = 'vendor_owner'
            session['username'] = vendor.username
            session['brand'] = vendor.brand_name
            return True, f"مرحباً بك في سوقك الذكي، {vendor.brand_name}."
        else:
            return False, "كلمة المرور غير صحيحة، يرجى المحاولة مرة أخرى."

    # --- [ الخطوة 2: فحص حسابات الموظفين (Staff) ] ---
    staff = VendorStaff.query.filter_by(username=username).first()
    
    if staff:
        # حساب الموظف موجود، الآن نفحص كلمة المرور
        if staff.password == password:
            session.clear()
            session['user_id'] = staff.vendor_id 
            session['role'] = 'vendor_staff'
            session['username'] = staff.username
            session['brand'] = staff.owner.brand_name
            return True, "تم دخول الموظف بنجاح إلى النظام اللامركزي."
        else:
            return False, "كلمة مرور الموظف غير صحيحة."

    # --- [ الخطوة 3: إذا لم يوجد الحساب نهائياً ] ---
    return False, "عذراً، هذا الحساب غير مسجل في المنصة اللامركزية لمحجوب أونلاين."
