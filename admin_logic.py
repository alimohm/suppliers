from flask import session, flash
from models import AdminUser

def verify_admin_credentials(username, password):
    """
    منطق مطابقة محمي ضد الانهيار ومتوافق مع الهوية الجديدة (علي محجوب)
    """
    try:
        # 1. البحث عن المدير في قاعدة البيانات باستخدام الاسم المدخل
        admin = AdminUser.query.filter_by(username=username).first()
        
        # 2. الفحص الأول: التحقق من وجود المستخدم
        if admin is None:
            flash("🚫 هذا المستخدم غير مسجل في المنصة اللامركزية.", "warning")
            return False
        
        # 3. الفحص الثاني: مطابقة كلمة المرور مع تحويلها لنص لمنع الانهيار
        if str(admin.password) != str(password):
            flash("⚠️ كلمة المرور غير صحيحة، يرجى المحاولة مرة أخرى.", "danger")
            return False

        # 4. حالة النجاح التام: إعداد الجلسة (Session)
        session['is_admin'] = True
        session['admin_user'] = admin.username # سيخزن "علي محجوب" هنا
        
        # رسالة الترحيب الملكية التي تظهر في الداشبورد
        flash(f"🛡️ تم تفعيل وصول برج المراقبة. مرحباً بك يا سيد {admin.username}", "success")
        return True

    except Exception as e:
        # طباعة الخطأ في سجلات السيرفر (Logs) لتسهيل التصحيح
        print(f"DEBUG ERROR IN ADMIN_LOGIC: {e}")
        flash("حدث خطأ تقني في أنظمة برج المراقبة، يرجى التحقق من قاعدة البيانات.", "danger")
        return False

def is_admin_logged_in():
    """التحقق مما إذا كان المدير مسجلاً دخوله حالياً"""
    return session.get('is_admin', False)

def logout_admin_logic():
    """تأمين الخروج ومسح بيانات الجلسة"""
    session.pop('is_admin', None)
    session.pop('admin_user', None)
    flash("🔒 تم تأمين الخروج من برج المراقبة بنجاح.", "info")
    return True
