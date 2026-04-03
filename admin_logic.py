from flask import session, flash
from models import AdminUser

def verify_admin_credentials(username, password):
    """
    منطق مطابقة محمي ضد الانهيار (Crash-Proof)
    """
    try:
        # 1. البحث عن المدير في قاعدة البيانات
        admin = AdminUser.query.filter_by(username=username).first()
        
        # 2. الفحص الأول: إذا لم يجد الاسم (هذا الجزء شغال عندك تمام)
        if admin is None:
            flash("🚫 هذا المستخدم غير مسجل في المنصة اللامركزية.", "warning")
            return False
        
        # 3. الفحص الثاني: مطابقة كلمة المرور (هنا كان يحدث الانهيار)
        # نستخدم التحقق المباشر مع التأكد من أن admin ليس فارغاً
        if str(admin.password) != str(password):
            flash("⚠️ كلمة المرور غير صحيحة، يرجى المحاولة مرة أخرى.", "danger")
            return False

        # 4. حالة النجاح التام
        session['is_admin'] = True
        session['admin_user'] = admin.username
        
        flash(f"🛡️ تم تفعيل وصول برج المراقبة. مرحباً بك يا سيد {admin.username}", "success")
        return True

    except Exception as e:
        # هذا الجزء يمنع الانهيار ويطبع الخطأ في الـ Logs لتعرفه
        print(f"DEBUG ERROR: {e}")
        flash("حدث خطأ تقني في برج المراقبة، يرجى مراجعة المبرمج.", "danger")
        return False

def is_admin_logged_in():
    return session.get('is_admin', False)

def logout_admin_logic():
    session.pop('is_admin', None)
    session.pop('admin_user', None)
    flash("🔒 تم تأمين الخروج من برج المراقبة.", "info")
    return True
