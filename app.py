import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

# 1. استيراد الإعدادات وقاعدة البيانات
from config import Config
from database import db, init_db

# 2. استيراد الجداول (ضروري جداً لإنشائها تلقائياً)
from models import AdminUser, Vendor, VendorStaff, Product, seed_system

# 3. استيراد المنطق (Logic) من الملفات المنفصلة
from vendor_logic import login_vendor, is_logged_in, can_see_wallet
from admin_logic import verify_admin_credentials, is_admin_logged_in

app = Flask(__name__)
app.config.from_object(Config)

# تهيئة قاعدة البيانات وربطها بالتطبيق
init_db(app)

# --- [ مرحلة التأسيس والتشغيل التلقائي ] ---
with app.app_context():
    # إنشاء الجداول إذا لم تكن موجودة
    db.create_all()
    # حقن الحسابات الأساسية (علي محجوب، محجوب أونلاين، موظف تجريبي)
    seed_system()
    print("✅ النظام جاهز: الجداول أُنشئت، والبيانات السيادية حُقنت بنجاح.")

# --- [ المسارات الأساسية - Routes ] ---

@app.route('/')
def index():
    """التوجيه الذكي بناءً على نوع الجلسة"""
    if is_admin_logged_in():
        return redirect(url_for('admin_dashboard'))
    if is_logged_in():
        return redirect(url_for('vendor_dashboard'))
    return redirect(url_for('vendor_login'))

# --- [ بوابة المورد وموظفيه ] ---

@app.route('/vendor/login', methods=['GET', 'POST'])
def vendor_login():
    if is_logged_in():
        return redirect(url_for('vendor_dashboard'))
    
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        # استدعاء المنطق من vendor_logic.py
        success, msg = login_vendor(u, p)
        
        if success:
            flash(msg, "success")
            return redirect(url_for('vendor_dashboard'))
        else:
            flash(msg, "danger")
            
    return render_template('vendor_login.html')

@app.route('/vendor/dashboard')
def vendor_dashboard():
    if not is_logged_in():
        return redirect(url_for('vendor_login'))
    
    # جلب بيانات المورد لعرضها
    vendor = Vendor.query.get(session.get('user_id'))
    # تمرير دالة التحقق من المحفظة للقالب (HTML)
    return render_template('dashboard.html', 
                           vendor=vendor, 
                           show_wallet=can_see_wallet())

# --- [ بوابة الإدارة العليا - علي محجوب ] ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if is_admin_logged_in():
        return redirect(url_for('admin_dashboard'))
        
    if request.method == 'POST':
        u = request.form.get('admin_user', '').strip()
        p = request.form.get('admin_pass', '').strip()
        
        # استدعاء المنطق من admin_logic.py
        success, msg = verify_admin_credentials(u, p)
        
        if success:
            flash(msg, "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash(msg, "danger")
            
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_admin_logged_in():
        return redirect(url_for('admin_login'))
    
    # علي محجوب يرى كل الموردين والمنتجات والمحافظ
    all_vendors = Vendor.query.all()
    return render_template('admin_dashboard.html', vendors=all_vendors)

# --- [ تسجيل الخروج ] ---

@app.route('/logout')
def logout():
    session.clear()
    flash("تم تسجيل الخروج. نراك قريباً في محجوب أونلاين.", "info")
    return redirect(url_for('index'))

# --- [ تشغيل السيرفر ] ---

if __name__ == '__main__':
    # دعم التشغيل المحلي وعلى سيرفرات مثل Heroku/Render
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
