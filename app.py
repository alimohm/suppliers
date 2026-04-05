import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db, User, Wallet, Product
import logic

app = Flask(__name__)
app.config.from_object(Config)

# تهيئة قاعدة البيانات عند الإقلاع (تنشئ الجداول وحساب الإدارة)
init_db(app)

# ---------------------------------------------------------
# 1. الموجه الذكي (Smart Router)
# ---------------------------------------------------------
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login_admin'))
    # توجيه المستخدم حسب صلاحيته (مدير أو مورد)
    return redirect(url_for('admin_dashboard' if session['role'] == 'admin' else 'vendor_dashboard'))

# ---------------------------------------------------------
# 2. بوابات الدخول والاعتماد
# ---------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        user = User.query.filter_by(username=u, password=p).first()
        if user:
            session.update({'user_id': user.id, 'username': u, 'role': user.role})
            return redirect(url_for('index'))
        # تم تصحيح الفاصلة هنا لضمان عمل السيرفر
        flash("بيانات الدخول غير صحيحة", "danger") 
    return render_template('login_admin.html') # ملف صفحة دخول الإدارة

# ---------------------------------------------------------
# 3. نوافذ الإدارة المنفصلة (Modular Admin Windows)
# ---------------------------------------------------------

# أ- نافذة الإحصائيات (الرئيسية)
@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin': return redirect(url_for('login_admin'))
    vendors = User.query.filter_by(role='vendor').all()
    total_mah = db.session.query(db.func.sum(Wallet.balance)).scalar() or 0
    return render_template('admin_dashboard.html', vendors=vendors, total_mah=total_mah)

# ب- نافذة الحسابات والاعتماد (تسجيل الموردين)
@app.route('/admin/accounts')
def admin_accounts():
    if session.get('role') != 'admin': return redirect(url_for('login_admin'))
    vendors = User.query.filter_by(role='vendor').all()
    return render_template('admin_accounts.html', vendors=vendors)

# ج- نافذة الرقابة المالية (المحافظ)
@app.route('/admin/wallets')
def admin_wallets():
    if session.get('role') != 'admin': return redirect(url_for('login_admin'))
    vendors = User.query.filter_by(role='vendor').all()
    return render_template('admin_wallets.html', vendors=vendors)

# ---------------------------------------------------------
# 4. لوحة المورد (Vendor Window)
# ---------------------------------------------------------
@app.route('/vendor/dashboard')
def vendor_dashboard():
    if session.get('role') != 'vendor': return redirect(url_for('login_admin'))
    user = User.query.get(session['user_id'])
    # استدعاء المحفظة والمنتجات الخاصة بالمورد
    return render_template('vendor_dashboard.html', wallet=user.wallet, products=user.products)

# ---------------------------------------------------------
# 5. محركات الحفظ والعمليات (Action Engines)
# ---------------------------------------------------------

# حفظ بيانات المورد الجديد في قاعدة البيانات
@app.route('/action/add-vendor', methods=['POST'])
def add_vendor():
    if session.get('role') != 'admin': return "غير مصرح", 403
    brand = request.form.get('brand')
    user = request.form.get('user')
    pwd = request.form.get('pwd')
    
    # استدعاء منطق الحفظ والتأسيس من ملف logic
    success, wallet_no = logic.add_new_vendor(brand, user, pwd)
    if success:
        flash(f"تم حفظ المورد {brand} وتفعيل محفظته: {wallet_no}", "success")
    else:
        flash("فشل الحفظ، الاسم موجود مسبقاً", "danger")
    return redirect(url_for('admin_accounts'))

# محرك التحويل المالي (MAH)
@app.route('/action/transfer', methods=['POST'])
def transfer():
    if 'user_id' not in session: return redirect(url_for('login_admin'))
    target = request.form.get('target')
    amount = float(request.form.get('amount', 0))
    success, msg = logic.execute_transfer(session['user_id'], target, amount, "تحويل يدوي")
    flash(msg, "success" if success else "danger")
    return redirect(url_for('vendor_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_admin'))

if __name__ == '__main__':
    # البورت المتوافق مع Railway
    app.run(host='0.0.0.0', port=8080)
