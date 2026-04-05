import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db, User, Wallet, Product
import logic

app = Flask(__name__)
app.config.from_object(Config)

# تهيئة قاعدة البيانات
init_db(app)

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login_admin'))
    return redirect(url_for('admin_dashboard' if session['role'] == 'admin' else 'vendor_dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        user = User.query.filter_by(username=u, password=p).first()
        if user:
            session.update({'user_id': user.id, 'username': u, 'role': user.role})
            return redirect(url_for('index'))
        # تم تصحيح الفاصلة هنا من (،) إلى (,)
        flash("بيانات الدخول غير صحيحة", "danger") 
    return render_template('login_admin.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin': return redirect(url_for('login_admin'))
    vendors = User.query.filter_by(role='vendor').all()
    total_mah = db.session.query(db.func.sum(Wallet.balance)).scalar() or 0
    products_count = Product.query.count()
    return render_template('admin_dashboard.html', vendors=vendors, total_mah=total_mah, products_count=products_count)

@app.route('/admin/accounts')
def admin_accounts():
    if session.get('role') != 'admin': return redirect(url_for('login_admin'))
    vendors = User.query.filter_by(role='vendor').all()
    return render_template('admin_accounts.html', vendors=vendors)

@app.route('/vendor/dashboard')
def vendor_dashboard():
    if session.get('role') != 'vendor': return redirect(url_for('login_admin'))
    user = User.query.get(session['user_id'])
    return render_template('vendor_dashboard.html', wallet=user.wallet, products=user.products)

@app.route('/action/add-vendor', methods=['POST'])
def add_vendor():
    if session.get('role') != 'admin': return "Unauthorized", 403
    brand = request.form.get('brand')
    user = request.form.get('user')
    pwd = request.form.get('pwd')
    logic.add_new_vendor(brand, user, pwd)
    flash(f"تم اعتماد المورد {brand} بنجاح", "success")
    return redirect(url_for('admin_accounts'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
