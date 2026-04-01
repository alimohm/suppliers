from database import db, Vendor
from flask import session

def verify_login(username, password):
    """
    وظيفة التحقق السيادي من الهوية
    تعمل كبوابة أمان قبل السماح بالدخول للهيكل
    """
    user = Vendor.query.filter_by(username=username).first()
    
    if not user:
        return {"status": False, "message": "عذراً، اسم المستخدم غير مسجل"}
    
    if user.password != password:
        return {"status": False, "message": "كلمة المرور غير صحيحة"}
    
    # إذا كانت البيانات صحيحة، يتم تجهيز بيانات الجلسة
    return {
        "status": True, 
        "user_id": user.id, 
        "owner_name": user.owner_name,
        "role": "admin" if user.username == "ali" else "vendor"
    }

def get_dashboard_stats(vendor_id):
    """
    محرك استخراج البيانات لـ لوحة الهيكل
    يستخرج الإحصائيات بسرعة SEO عالية
    """
    # هنا يتم وضع منطق جلب المبيعات، الطلبات، والمنتجات مستقبلاً
    stats = {
        "orders_count": 0,
        "total_sales": "0.00",
        "active_products": 0,
        "messages_count": 0
    }
    return stats

def is_authorized(required_role="vendor"):
    """
    درع حماية المسارات
    يتحقق مما إذا كان المستخدم يمتلك الصلاحية للوصول لرابط معين
    """
    if 'vendor_id' not in session:
        return False
    
    user_role = session.get('role', 'vendor')
    if required_role == "admin" and user_role != "admin":
        return False
        
    return True
