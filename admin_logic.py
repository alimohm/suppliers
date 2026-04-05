from database import db
from models import AdminUser, Vendor, Wallet, Transaction
# بقية الكود...

# 1. التحقق من بيانات المالك (هذه هي الدالة التي يطلبها السجل في صورك)
def verify_admin_credentials(u, p):
    admin = AdminUser.query.filter_by(username=u.strip()).first()
    if admin and admin.password == p:
        return True, "تم الدخول بنجاح إلى برج المراقبة ✨"
    return False, "بيانات الدخول غير صحيحة."

# 2. جلب إحصائيات لوحة التحكم
def get_admin_stats():
    return {
        'pending': Vendor.query.filter_by(is_active=False).count(),
        'active': Vendor.query.filter_by(is_active=True).count(),
        'total_balance': db.session.query(db.func.sum(Wallet.balance)).scalar() or 0.0
    }

# 3. الدالة التي تطلبها صفحة الحسابات (برج المراقبة)
def manage_accounts_logic():
    return Vendor.query.order_by(Vendor.id.desc()).all()

# 4. جلب بيانات الموردين مع الفلترة
def get_dashboard_data(filter_type=None):
    if filter_type == 'pending':
        return Vendor.query.filter_by(is_active=False).order_by(Vendor.id.desc()).all()
    return Vendor.query.order_by(Vendor.id.desc()).all()

# 5. دالة القبول (تفعيل + محفظة + أول حركة في كشف الحساب)
def approve_vendor_logic(vendor_id):
    vendor = Vendor.query.get(vendor_id)
    if not vendor or vendor.is_active:
        return False, "المورد غير موجود أو مفعل مسبقاً."

    try:
        vendor.is_active = True
        vendor.status = "نشط"
        
        if not vendor.wallet:
            new_wallet = Wallet(vendor_id=vendor.id)
            db.session.add(new_wallet)
            db.session.flush()
            
            # تسجيل الحركة الكاملة (بداية كشف الحساب)
            first_tx = Transaction(
                wallet_id=new_wallet.id,
                trans_type="تأسيس",
                amount=0.0,
                balance_after=0.0,
                description="افتتاح الحساب المالي في محجوب أونلاين"
            )
            db.session.add(first_tx)
        
        db.session.commit()
        return True, f"تم منح السيادة للمورد {vendor.brand_name} بنجاح."
    except Exception as e:
        db.session.rollback()
        return False, f"خطأ تقني: {str(e)}"

# 6. إضافة مورد يدوياً
def create_vendor_logic():
    u = request.form.get('username')
    bn = request.form.get('brand_name')
    p = request.form.get('password')
    
    if Vendor.query.filter_by(username=u).first():
        return False, "اسم المستخدم مسجل مسبقاً."
    
    try:
        new_v = Vendor(username=u, brand_name=bn, password=p, is_active=True, status="نشط")
        db.session.add(new_v)
        db.session.flush()
        
        w = Wallet(vendor_id=new_v.id)
        db.session.add(w)
        db.session.commit()
        return True, "تم تسجيل وتفعيل المورد بنجاح."
    except Exception as e:
        db.session.rollback()
        return False, f"خطأ: {str(e)}"
