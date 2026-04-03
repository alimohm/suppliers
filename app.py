import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

# --- استيراد المكونات اللامركزية للمشروع ---
from config import Config
from database import db, init_db
from models import Product, Vendor, AdminUser, seed_admin
from logic import login_vendor, is_logged_in
from admin_logic import is_admin_logged_in, verify_admin_credentials, logout_admin_logic

app = Flask(__name__)
app.config.from_object(Config)

# تفعيل قاعدة البيانات
init_db(app)
with app.app_context():
    db.create_all()
    seed_admin() # التأكد من وجود حسابك "صبري" كمسؤول

# ==========================================
# --- 1. نظام دخول الموردين (Vendor Login) ---
# ==========================================

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    # إذا كان المورد مسجلاً دخوله بالفعل، وجهه فوراً للداشبورد
    if is_logged_in(): 
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        if login_vendor(u, p):
            flash("مرحباً بك في سوقك الذكي", "success")
            return redirect(url_for('dashboard')) # التحويل الفعلي لصفحة المورد
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """لوحة تحكم المورد - تستدعي الهيكل العام"""
    if not is_logged_in(): 
        return redirect(url_for('login_page'))
    
    vendor = Vendor.query.filter_by(username=session['username']).first()
    my_products = Product.query.filter_by(brand=vendor.brand_name).all()
    
    return render_template('dashboard.html', vendor=vendor, products=my_products)


# ==========================================
# --- 2. نظام دخول الإدارة (Admin Login) ---
# ==========================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login_route():
    # إذا كان "صبري" مسجلاً دخوله، وجهه لبرج المراقبة
    if is_admin_logged_in(): 
        return redirect(url_for('admin_dashboard_route'))
        
    if request.method == 'POST':
        u = request.form.get('admin_user')
        p = request.form.get('admin_pass')
        if verify_admin_credentials(u, p):
            # تم التحقق -> الآن نقوم بالتحويل (Redirect)
            return redirect(url_for('admin_dashboard_route'))
            
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard_route():
    """لوحة تحكم الإدارة (برج المراقبة) - تستدعي الهيكل العام"""
    if not is_admin_logged_in(): 
        return redirect(url_for('admin_login_route'))
    
    all_vendors = Vendor.query.all()
    pending_items = Product.query.filter_by(status='pending').all()
    
    # هنا يتم استدعاء ملف admin_dashboard.html الذي بدوره "يمدد" layout.html
    return render_template('admin_dashboard.html', 
                           vendors=all_vendors, 
                           pending_count=len(pending_items),
                           pending_items=pending_items)


# ==========================================
# --- 3. عمليات الخروج والنظام ---
# ==========================================

@app.route('/')
def index():
    return redirect(url_for('login_page'))

@app.route('/logout')
def logout_route():
    session.clear()
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
