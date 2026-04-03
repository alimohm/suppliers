from flask import session
from werkzeug.security import check_password_hash
# استيراد نموذج الأدمن وقاعدة البيانات (تأكد من المسارات حسب مشروعك)
from models import AdminUser
from database import db

def verify_admin_credentials(username, password):
    try:
        # 1. البحث في سجلات برج المراقبة (الإدارة)
        admin = AdminUser.query.filter_by(username=username).first()

        # 2. التحقق من الهوية الرقمية
        if not admin:
            return False, "فشل تأمين بوابة الإدارة: المستخدم غير معرّف في سجلات السيادة."

        # 3. فحص التشفير (تأمين البوابة)
        if not check_password_hash(admin.password, password):
            return False, "فشل تأمين بوابة الإدارة: كلمة المرور غير مطابقة للمفاتيح المشفرة."

        # 4. تفعيل السيادة (الجلسة)
        session.clear()  # ضروري جداً لضمان عدم تداخل صلاحيات المورد مع الأدمن
        session['admin_id'] = admin.id
        session['username'] = admin.username
        session['role'] = 'admin'
        
        return True, "تم تفعيل الوصول إلى برج المراقبة السيادي."

    except Exception as e:
        # حماية النظام من الانهيار في حال فشل الاتصال بالقاعدة
        return False, f"عطل فني في بوابة الإدارة: {str(e)}"

def is_admin_logged_in():
    """التحقق من صلاحيات المسؤول الحالية"""
    return session.get('role') == 'admin' and 'admin_id' in session

def logout_admin_logic():
    """تأمين الخروج وإلغاء صلاحيات برج المراقبة"""
    session.clear()
    return True
