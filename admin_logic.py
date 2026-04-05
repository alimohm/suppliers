from flask import session, request
from models import AdminUser, Vendor, Wallet, db

def verify_admin_credentials(u, p):
    """
    تحقق منطقي لدخول المسؤول وتهيئة الجلسة السيادية
    """
    clean_username = u.strip() if u else ""
    
    if not clean_username or not p:
        return False, "يرجى إدخال بيانات الدخول كاملة."

    # البحث في قاعدة البيانات عن المسؤول
    admin = AdminUser.query.filter_by(username=clean_username).first()
    
    if not admin:
        return False, "هذا الاسم غير مسجل في المنصة."

    if admin.password != p:
        return False, "كلمة المرور غير صحيحة."

    # تثبيت الجلسة
    session.clear()
    session['admin_id'] = admin.id
    session['role'] = 'super_admin'
    session['username'] = admin.username
    
    return True, "تم التحقق بنجاح. مرحباً بك في مركز القيادة."

def get_admin_stats():
    """
    دالة مخصصة للوحة الرئيسية (Dashboard) لجلب الأرقام فقط
    بدون عرض نماذج التسجيل أو الجداول الطويلة
    """
    stats = {
        'total_vendors': Vendor.query.count(),
        'active_wallets': Wallet.query.count(),
        # يمكنك إضافة المزيد من الإحصائيات هنا (مثل إجمالي العمليات)
    }
    return stats

def manage_accounts_logic():
    """
    جلب كافة الموردين لصفحة 'اعتماد الموردين' حصراً
    """
    return Vendor.query.order_by(Vendor.id.desc()).all()

def create_vendor_logic():
    """
    المنطق السيادي لإنشاء مورد وتفعيل محفظته تلقائياً في قاعدة البيانات
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        brand_name = request.form.get('brand_name', '').strip()
        password = request.form.get('password', '').strip()

        # فحص التكرار في قاعدة البيانات
        if Vendor.query.filter_by(username=username).first():
            return False, "اسم المستخدم هذا محجوز مسبقاً."

        # 1. إنشاء سجل المورد الجديد
        new_vendor = Vendor(
            username=username,
            brand_name=brand_name,
            password=password, 
            status="نشط",
            is_active=True
        )
        
        try:
            db.session.add(new_vendor)
            db.session.flush() # الحصول على المعرف ID للمورد قبل الحفظ النهائي لربط المحفظة

            # 2. توليد المحفظة السيادية تلقائياً (MAH-XXXX) للمورد الجديد
            new_wallet = Wallet(vendor_id=new_vendor.id)
            db.session.add(new_wallet)
            
            db.session.commit() # حفظ التغييرات نهائياً في قاعدة البيانات
            return True, f"تم اعتماد {brand_name} وتفعيل السيادة المالية بنجاح."
            
        except Exception as e:
            db.session.rollback() # التراجع في حال حدوث أي خطأ تقني
            return False, f"حدث خطأ في قاعدة البيانات: {str(e)}"

    return False, "طلب غير صالح."
