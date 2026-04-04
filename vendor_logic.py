from flask import session
from models import Vendor, VendorStaff

def login_vendor(u, p):
    """
    منطق تسجيل الدخول الموحد للموردين (الملاك والموظفين)
    """
    # تنظيف المدخلات من المسافات الزائدة (لحماية الدخول)
    username = u.strip()
    password = p.strip()

    if not username or not password:
        return False, "يرجى إدخال اسم المستخدم وكلمة المرور."

    # --- [ 1. فحص سجلات الملاك (Vendor Owners) ] ---
    vendor = Vendor.query.filter_by(username=username).first()
    
    if vendor:
        # ملاحظة: نستخدم المقارنة المباشرة لتتوافق مع دالة seed_system الحالية
        if vendor.password == password:
            session.clear()
            session['user_id'] = vendor.id
            session['role'] = 'vendor_owner' # دور المالك (يرى المحفظة)
            session['username'] = vendor.username
            session['brand'] = vendor.brand_name
            return True, "مرحباً بك في نظامك الإداري الملكي."
        else:
            return False, "كلمة المرور غير صحيحة."

    # --- [ 2. فحص سجلات موظفي الموردين (Vendor Staff) ] ---
    staff = VendorStaff.query.filter_by(username=username).first()
    
    if staff:
        if staff.password == password:
            session.clear()
            # ربط جلسة الموظف بمعرف المورد (المحل) الذي يعمل لديه
            session['user_id'] = staff.vendor_id 
            session['role'] = 'vendor_staff' # دور الموظف (صلاحيات محدودة)
            session['username'] = staff.username
            # جلب اسم البراند من حساب المالك المرتبط
            session['brand'] = staff.owner.brand_name 
            return True, "تم دخول الموظف بنجاح إلى منصة العمل."
        else:
            return False, "كلمة المرور للموظف غير صحيحة."

    # في حال لم يتم العثور على أي تطابق
    return False, "بيانات الدخول غير مسجلة في نظام محجوب أونلاين."
