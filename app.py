import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db, Vendor
import logic  # محرك السرعة والـ SEO والصلاحيات
import finance  # المحرك المالي الدقيق بنظام Decimal

# 1. تهيئة التطبيق والقاعدة مع إعدادات الاستقرار (The Core)
app = Flask(__name__)
app.config.from_object(Config)
init_db(app)

# 2. ضمان وجود الجداول والحساب السيادي عند التشغيل
with app.app_context():
    db.create_all() # إنشاء الجداول فوراً لمنع الأخطاء التقنية
    
    # التأكد من وجود حساب المالك "ali" كقاعدة استقرار
    if not Vendor.query.filter_by(username="ali").first():
        default_vendor = Vendor(
            username="ali", 
            password="123", 
            owner_name="علي محجوب", 
            brand_name="محجوب أونلاين"
        )
        db.session.add(default_vendor)
        db.session.commit()

# 3. توجيه الصفحة الرئيسية (التحويل الذكي)
@app.route('/')
def home():
    # إذا كانت الجلسة نشطة، اذهب للهيكل مباشرة
    if 'vendor_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# 4. بوابة الدخول الملكية (المعكوسة والآمنة)
@app.route('/login', methods=['GET', 'POST'])
def login():
    # منع المستخدم المسجل من رؤية صفحة الدخول مرة أخرى
    if 'vendor_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # البحث والتحقق عبر 'عقل النظام' في logic.py
        user = Vendor.query.filter_by(username=username).first()
        
        if not user:
            flash("عذراً، اسم المستخدم هذا غير مسجل لدينا", "error")
        elif user.password != password:
            flash("خطأ في بيانات الدخول: كلمة المرور غير صحيحة", "error")
        else:
            # نجاح العملية: إنشاء الجلسة وتفعيل نظام الصلاحيات
            session.permanent = True # بقاء الجلسة نشطة (Persistent)
            session['vendor_id'] = user.id
            session['role'] = "admin" if user.username == "ali" else "vendor"
            
            flash(f"مرحباً بك في عرشك الرقمي، {user.owner_name}", "success")
            return redirect(url_for('dashboard')) # التحويل الفوري للهيكل
            
    return render_template('login.html')

# 5. لوحة الهيكل (Dashboard) - مركز العمليات الأرجواني
@app.route('/dashboard')
def dashboard():
    # الدرع الواقي: حماية الرابط من الدخول غير المصرح به
    if 'vendor_id' not in session:
        return redirect(url_for('login'))
        
    vendor = Vendor.query.get(session['vendor_id'])
    
    # استدعاء بيانات الهيكل بتنسيق SEO الصديق من logic.py
    dashboard_data = logic.get_dashboard_stats(vendor.id)
    
    # عرض الواجهة التي تحتوي على "الخطوات الأربع"
    return render_template('dashboard.html', vendor=vendor, stats=dashboard_data)

# 6. تسجيل الخروج وتطهير الجلسة
@app.route('/logout')
def logout():
    session.clear() # تدمير كافة بيانات الجلسة للأمان
    flash("تم تسجيل الخروج بنجاح. ننتظرك قريباً.", "info")
    return redirect(url_for('login'))

# 7. تشغيل السيرفر الملكي مع ضغط البيانات
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    # تشغيل السيرفر ليكون متوافقاً مع الهواتف والتابلت
    app.run(host='0.0.0.0', port=port, debug=False)
