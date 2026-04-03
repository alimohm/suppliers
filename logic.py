# logic.py
from models import Vendor
from werkzeug.security import check_password_hash
from flask import session

def login_vendor(username, password):
    # البحث في قاعدة بيانات الموردين المرتبطة
    vendor = Vendor.query.filter_by(username=username).first()

    if not vendor:
        return False, "المستخدم غير مسجل في المنصة اللامركزية."

    if not check_password_hash(vendor.password, password):
        return False, "فشل تأمين البوابة: كلمة المرور غير صحيحة."

    # --- فحص الحالة السيادية للمورد ---
    status = vendor.status.lower() if vendor.status else 'pending'

    if status == 'blocked':
        return False, "وصول مرفوض: تم حظر حسابك بقرار سيادي."
    
    elif status == 'restricted':
        return False, "حساب مقيد: صلاحياتك معلقة حالياً."
    
    elif status == 'pending':
        return False, "الدخول معلق: حسابك لا يزال تحت المراجعة."

    # إذا مر من كل الفحوصات:
    session['user_id'] = vendor.id
    session['username'] = vendor.username
    session['role'] = 'vendor'
    
    if status == 'under_surveillance':
        session['surveillance_mode'] = True
        return True, "تنبيه: أنت الآن تحت نظام الرقابة الرقمية المستمرة."

    return True, "تم الدخول بنجاح."
