import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

# --- 1. تعريف التطبيق السيادي ---
app = Flask(__name__) #

# --- 2. استدعاء المحركات (بناءً على نماذج models.py الجديدة) ---
from config import Config
from database import db, init_db
from models import Product, Vendor, AdminUser, seed_admin #

# استيراد المنطق (تأكد أن الدوال داخل هذه الملفات تطابق أسماء الجداول)
from logic import login_vendor, is_logged_in 
from admin_logic import is_admin_logged_in, verify_admin_credentials 

app.config.from_object(Config)
init_db(app)

with app.app_context():
    # إنشاء الجداول وتحديثها (status, wallet_address)
    db.create_all() 
    # حقن بياناتك (علي محجوب) كأدمن ومورد في نفس الوقت
    seed_admin() 

# ==========================================
# --- مسارات الإدارة (أي شيء فيه Admin) ---
# ==========================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if is_admin_logged_in(): return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        u = request.form.get('admin_user', '').strip()
        p = request.form.get('admin_pass', '').strip()
        
        # التحقق من جدول AdminUser
        success, message = verify_admin_credentials(u, p)
        if success:
            flash(message, "success")
            return redirect(url_for('admin_dashboard'))
        flash(message, "danger")
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_admin_logged_in(): return redirect(url_for('admin_login'))
    # جلب كافة الموردين والمنتجات المعلقة للموافقة
    all_vendors = Vendor.query.all()
    pending_prods = Product.query.filter_by(status='pending').all()
    return render_template('admin_dashboard.html', vendors=all_vendors, pending_count=len(pending_prods))

# ==========================================
# --- مسارات المورد (أي شيء بدون Admin) ---
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in(): return redirect(url_for('vendor_dashboard'))
    if request.method == 'POST':
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        
        # التحقق من جدول Vendor
        success, message = login_vendor(u, p)
        if success:
            flash(message, "success")
            return redirect(url_for('vendor_dashboard'))
        flash(message, "danger")
    return render_template('login.html')

@app.route('/dashboard')
def vendor_dashboard():
    if not is_logged_in(): return redirect(url_for('login_page'))
    vendor = Vendor.query.get(session.get('user_id'))
    # عرض منتجات المورد فقط
    products = Product.query.filter_by(vendor_id=vendor.id).all()
    return render_template('dashboard.html', vendor=vendor, products=products)

# الخروج العام
@app.route('/logout')
def logout():
    session.clear()
    flash("تم تأمين كافة البوابات بنجاح.", "info")
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080)) #
    app.run(host='0.0.0.0', port=port)
