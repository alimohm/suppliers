import os
import random
from flask import session, request
from models import AdminUser, Vendor, Wallet, VendorStaff, db

# 1. دالة تسجيل طلب مورد جديد (من الموقع العام)
def register_vendor_request():
    """هذه الدالة تستقبل الطلب وتضعه في حالة 'معلق'"""
    if request.method == 'POST':
        u = request.form.get('username')
        bn = request.form.get('brand_name')
        p = request.form.get('password')
        ph = request.form.get('phone')
        
        # التأكد من عدم تكرار البيانات المؤندكسة
        if Vendor.query.filter_by(username=u).first():
            return False, "اسم المستخدم محجوز مسبقاً."

        # إنشاء سجل المورد بحالة (معلق) وغير نشط
        new_v = Vendor(
            username=u,
            brand_name=bn,
            password=p,
            phone=ph,
            status="معلق", # الحالة المنطقية الأولى
            is_active=False # لا يمكنه الدخول بعد
        )
        
        try:
            db.session.add(new_v)
            db.session.commit()
            return True, "تم إرسال طلبك بنجاح، سيتم مراجعته سيادياً."
        except Exception as e:
            db.session.rollback()
            return False, f"خطأ في التسجيل: {str(e)}"
    return False, "طلب غير صالح."

# 2. جلب الطلبات لبرج المراقبة (مرتبة بالأحدث)
def manage_accounts_logic():
    """جلب كل الموردين ليتمكن المالك من رؤية المعلقين أولاً"""
    return Vendor.query.order_by(Vendor.is_active.asc(), Vendor.id.desc()).all()

# 3. دالة القبول والتحقق (الزر الذي ستضغطه أنت)
def approve_vendor_logic(vendor_id):
    """تحويل الحالة من معلق إلى نشط وتفعيل المحفظة"""
    vendor = Vendor.query.get(vendor_id)
    
    if not vendor:
        return False, "المورد غير موجود في السجلات."
    
    if vendor.is_active:
        return False, "هذا المورد معتمد ونشط بالفعل."

    # التفعيل المنطقي
    vendor.is_active = True
    vendor.status = "نشط"
    
    # الربط بالمحفظة السيادية فوراً (بناءً على الجداول)
    if not vendor.wallet:
        new_wallet = Wallet(vendor_id=vendor.id)
        db.session.add(new_wallet)
    
    try:
        db.session.commit()
        return True, f"تم قبول المورد {vendor.brand_name} وتفعيل محفظته MAH."
    except Exception as e:
        db.session.rollback()
        return False, "فشل في تحديث الحالة."

# 4. تحقق دخول الأطراف الثلاثة (استخدام الإندكس)
def verify_admin_credentials(u, p):
    admin = AdminUser.query.filter_by(username=u.strip()).first()
    if admin and admin.password == p:
        session.clear()
        session['user_id'], session['role'] = admin.id, 'super_admin'
        return True, "دخول سيادي ناجح."
    return False, "خطأ في بيانات المالك."

def verify_vendor_credentials(u, p):
    vendor = Vendor.query.filter_by(username=u.strip()).first()
    if vendor and vendor.password == p:
        if not vendor.is_active:
            return False, "عذراً، طلبك لا يزال قيد المراجعة."
        session.clear()
        session['user_id'], session['role'] = vendor.id, 'vendor'
        return True, "دخول المورد ناجح."
    return False, "خطأ في بيانات المورد."

# 5. إحصائيات برج المراقبة (لمعرفة حجم العمل)
def get_admin_stats():
    return {
        'pending': Vendor.query.filter_by(is_active=False).count(),
        'active': Vendor.query.filter_by(is_active=True).count(),
        'total_balance': db.session.query(db.func.sum(Wallet.balance)).scalar() or 0
    }
