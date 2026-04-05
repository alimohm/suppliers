from models import AdminUser, Vendor, Wallet, Transaction, db
from flask import request

# 1. التحقق من بيانات المالك (هذه الدالة المفقودة التي تسببت في الانهيار)
def verify_admin_credentials(u, p):
    admin = AdminUser.query.filter_by(username=u.strip()).first()
    if admin and admin.password == p:
        return True, "دخول سيادي ناجح."
    return False, "خطأ في بيانات المالك."

# 2. جلب إحصائيات برج المراقبة
def get_admin_stats():
    return {
        'pending': Vendor.query.filter_by(is_active=False).count(),
        'active': Vendor.query.filter_by(is_active=True).count(),
        'total_balance': db.session.query(db.func.sum(Wallet.balance)).scalar() or 0
    }

# 3. جلب بيانات الموردين لبرج المراقبة (مع دعم الفلترة)
def get_dashboard_data(filter_type=None):
    if filter_type == 'pending':
        return Vendor.query.filter_by(is_active=False).order_by(Vendor.id.desc()).all()
    return Vendor.query.order_by(Vendor.id.desc()).all()

# 4. منطق القبول والتحقق (تفعيل المورد وكشف الحساب)
def approve_vendor_logic(vendor_id):
    vendor = Vendor.query.get(vendor_id)
    if not vendor or vendor.is_active:
        return False, "المورد غير موجود أو نشط بالفعل."

    vendor.is_active = True
    vendor.status = "نشط"
    
    # ربط المحفظة
    if not vendor.wallet:
        new_wallet = Wallet(vendor_id=vendor.id)
        db.session.add(new_wallet)
        db.session.flush() # للحصول على ID المحفظة
        
        # تسجيل أول حركة في كشف الحساب
        first_tx = Transaction(
            wallet_id=new_wallet.id,
            trans_type="تأسيس",
            amount=0.0,
            balance_after=0.0,
            description="تفعيل الحساب السيادي في محجوب أونلاين"
        )
        db.session.add(first_tx)
    
    try:
        db.session.commit()
        return True, f"تم قبول المورد {vendor.brand_name} وتفعيل محفظته."
    except Exception as e:
        db.session.rollback()
        return False, f"خطأ في قاعدة البيانات: {str(e)}"

# 5. تسجيل مورد يدوي (إذا كنت تستخدمه في app.py)
def create_vendor_logic():
    u = request.form.get('username')
    bn = request.form.get('brand_name')
    p = request.form.get('password')
    
    if Vendor.query.filter_by(username=u).first():
        return False, "اسم المستخدم محجوز."
    
    new_v = Vendor(username=u, brand_name=bn, password=p, is_active=True, status="نشط")
    db.session.add(new_v)
    db.session.flush()
    db.session.add(Wallet(vendor_id=new_v.id))
    db.session.commit()
    return True, "تم إضافة المورد يدوياً."
