import os
from flask import session, request
from models import AdminUser, Vendor, Wallet, db
from werkzeug.utils import secure_filename

# إعدادات رفع الملفات (تأكد من وجود المجلدات في static/uploads)
UPLOAD_FOLDER = 'static/uploads'

def verify_admin_credentials(u, p):
    """تحقق منطقي ذكي لدخول المسؤول مع تنظيف الجلسة"""
    clean_username = u.strip() if u else ""
    if not clean_username or not p:
        return False, "يرجى إدخال بيانات الدخول كاملة."

    # الاستعلام مستفيد من الـ Index الذي أضفناه في models.py
    admin = AdminUser.query.filter(AdminUser.username == clean_username).first()
    
    if not admin:
        return False, "هذا الاسم غير مسجل في المنصة اللامركزية."

    if admin.password != p:
        return False, "كلمة المرور غير صحيحة، يرجى المحاولة مرة أخرى."

    session.clear()
    session['admin_id'] = admin.id
    session['role'] = 'super_admin'
    session['username'] = admin.username
    
    return True, "تم التحقق بنجاح. مرحباً بك في مركز القيادة."

def get_admin_stats():
    """دالة الإحصائيات - سريعة جداً بفضل استخدام count() المباشر"""
    try:
        total_v = db.session.query(Vendor).count()
        total_w = db.session.query(Wallet).count()
        return {'total_vendors': total_v, 'active_wallets': total_w}
    except Exception as e:
        print(f"⚠️ خطأ في جلب الإحصائيات: {e}")
        return {'total_vendors': 0, 'active_wallets': 0}

def create_vendor_logic():
    """
    إنشاء مورد جديد مع دعم رفع الصور (الهوية/السجل) 
    وتفعيل محفظته MAH تلقائياً.
    """
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        bn = request.form.get('brand_name', '').strip()
        p = request.form.get('password', '').strip()
        ph = request.form.get('phone', '').strip()

        if not u or not p:
            return False, "اسم المستخدم وكلمة المرور متطلبات أساسية."

        if Vendor.query.filter_by(username=u).first():
            return False, "اسم المستخدم هذا محجوز مسبقاً."

        try:
            # معالجة رفع الصور السيادية
            id_path, reg_path = None, None
            
            if 'id_card' in request.files:
                file = request.files['id_card']
                if file and file.filename != '':
                    filename = secure_filename(f"id_{u}_{file.filename}")
                    id_path = os.path.join('uploads/ids', filename)
                    file.save(os.path.join('static', id_path))

            # 1. إنشاء سجل المورد
            new_vendor = Vendor(
                username=u, brand_name=bn, password=p, 
                phone=ph, id_card_image=id_path,
                status="نشط", is_active=True # تفعيل فوري عند الإضافة من قبل الآدمن
            )
            db.session.add(new_vendor)
            db.session.flush() 

            # 2. توليد المحفظة السيادية
            new_wallet = Wallet(vendor_id=new_vendor.id)
            db.session.add(new_wallet)
            
            db.session.commit()
            return True, f"✅ تم اعتماد {bn} بنجاح."
            
        except Exception as e:
            db.session.rollback()
            return False, f"❌ خطأ تقني: {str(e)}"
    return False, "طلب غير صالح."

def activate_existing_vendor(vendor_id):
    """
    هذه الدالة هي التي تعمل عند الضغط على زر 'طلب تفعيل' 
    للموردين المسجلين مسبقاً (الذين حالتهم معلق).
    """
    try:
        vendor = Vendor.query.get(vendor_id)
        if not vendor:
            return False, "المورد غير موجود."

        vendor.is_active = True
        vendor.status = "نشط"

        # التأكد من وجود محفظة، وإذا لم توجد ننشئها فوراً
        if not vendor.wallet:
            new_wallet = Wallet(vendor_id=vendor.id)
            db.session.add(new_wallet)

        db.session.commit()
        return True, f"🚀 تم منح السيادة الكاملة لـ {vendor.brand_name}"
    except Exception as e:
        db.session.rollback()
        return False, f"❌ فشل التنشيط: {str(e)}"
