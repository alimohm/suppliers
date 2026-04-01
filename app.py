import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db, Vendor

# 1. تهيئة التطبيق والارتباط بقاعدة البيانات
app = Flask(__name__)
app.config.from_object(Config)
init_db(app)

# 2. منطق الحماية والتحقق عند بدء التشغيل
with app.app_context():
    # إنشاء الجداول فوراً لمنع خطأ "no such table"
    db.create_all() 
    
    # التأكد من وجود حسابك الشخصي كبيانات افتراضية للدخول
    if not Vendor.query.filter_by(username="ali").first():
        default_vendor = Vendor(
            username="ali", 
            password="123", 
            owner_name="علي محجوب", 
            brand_name="محجوب أونلاين"
        )
        db.session.add(default_vendor)
        db.session.commit()

# 3. توجيه الصفحة الرئيسية إلى بوابة الدخول
@app.route('/')
def home():
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

# 4. بوابة الدخول الملكية (المنطق الكامل)
@app.route('/login', methods=['GET', 'POST'])
def login():
    # في حالة محاولة الدخول (إرسال النموذج)
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # البحث عن المستخدم في قاعدة البيانات
        user = Vendor.query.filter_by(username=username).first()
        
        # التحقق من صحة البيانات وإظهار التنبيهات الاحترافية
        if not user:
            flash("عذراً، اسم المستخدم هذا غير مسجل لدينا", "error")
        elif user.password != password:
            flash("خطأ في بيانات الدخول: كلمة المرور غير صحيحة", "error")
        else:
            # نجاح العملية: إنشاء الجلسة والتحويل للوحة التحكم
            session['vendor_id'] = user.id
            return redirect(url_for('dashboard'))
            
    # عرض الواجهة الاحترافية (GET request)
    return render_template('login.html')

# 5. رابط لوحة التحكم (الهدف بعد الدخول)
@app.route('/dashboard')
def dashboard():
    # حماية الرابط: منع الدخول المباشر بدون تسجيل
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
        
    vendor = Vendor.query.get(session['vendor_id'])
    return render_template('dashboard.html', vendor=vendor)

# 6. تسجيل الخروج وتدمير الجلسة
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 7. تشغيل السيرفر الملكي
if __name__ == "__main__":
    # استخدام المنفذ 8080 المتوافق مع الاستضافة
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
