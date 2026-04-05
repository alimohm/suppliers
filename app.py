import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db, User, Wallet, Product
import logic

app = Flask(__name__)
app.config.from_object(Config)

# تهيئة قاعدة البيانات عند تشغيل التطبيق
init_db(app)

# ---------------------------------------------------------
# 1. بوابة التوجيه الذكية (Home Router)
# ---------------------------------------------------------
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login_admin'))
    
    if session.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('vendor_dashboard'))

# ---------------------------------------------------------
# 2. بوابات تسجيل الدخول (Login Gates)
# ---------------------------------------------------------

# دخول المدير (علي محجوب)
@app.route('/login', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        user = User.query.filter_by(username=u, password=p, role='admin').first()
        if user:
            session.update({'user_id': user.id, 'username': u, 'role': 'admin'})
            return redirect(url_for('admin_dashboard'))
        flash("خطأ في بيانات دخول المدير", "danger")
    return render_template('login_admin.html')

# دخول الموردين (الشركاء)
@app.route('/login/vendor', methods=['GET', 'POST'])
def login_vendor():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        user = User.query.filter_by(username=u, password=p, role='vendor').first()
        if user:
            session.update({'user_id': user.id, 'username': u, 'role': 'vendor'})
            return redirect(url_for('vendor_dashboard'))
        flash("خطأ في بيانات دخول المورد", "danger")
    return render_template('login_vendor.html')

# ---------------------------------------------------------
# 3. لوحات التحكم الإدارية (Admin Windows)
# ---------------------------------------------------------

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('login_admin'))
    
    vendors = User.query.filter_by(role='vendor').all()
    # حساب إجمالي الـ MAH في النظام
    total_mah = db.session.query(db.func.sum(Wallet.balance)).scalar() or 0
    return render_template('admin_dashboard.html', vendors=vendors, total_mah=total_mah)

@app.route('/admin/accounts')
def admin_accounts():
    if session.get('role') != 'admin':
        return redirect(url_for('login_admin'))
    
    vendors = User.query.filter_by(role='vendor').all()
    return render_template('admin_accounts.html', vendors=vendors)

# ---------------------------------------------------------
# 4. لوحة تحكم المورد (Vendor Window)
# ---------------------------------------------------------

@app.route('/vendor/dashboard')
def vendor_dashboard():
    if session.get('role') != 'vendor':
        return redirect(url_for('login_vendor'))
    
    user = User.query.get(session['user_id'])
    return render_template('vendor_dashboard.html', wallet=user.wallet, products=user.products)

# ---------------------------------------------------------
# 5. محركات الأفعال (Action Engines)
# ---------------------------------------------------------

# إضافة
