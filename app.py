import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db, User, Wallet, Product
import logic

app = Flask(__name__)
app.config.from_object(Config)

# تهيئة قاعدة البيانات عند التشغيل
init_db(app)

@app.route('/')
def index():
    if 'user_id' not in session: return redirect(url_for('login_admin'))
    return redirect(url_for('admin_dashboard' if session['role'] == 'admin' else 'vendor_dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        u, p = request.form.get('username'), request.form.get('password')
        user = User.query.filter_by(username=u, password=p).first()
        if user:
            session.update({'user_id': user.id, 'username': u, 'role': user.role})
            return redirect(url_for('index'))
        flash("بيانات الدخول غير صحيحة", "danger")
    return render_template('login_admin.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin': return redirect(url_for('login_admin'))
    vendors = User.query.filter_by(role='vendor').all()
    total_mah = db.session.query(db.func.sum(Wallet.balance)).scalar() or 0
    return render_template('admin_dashboard.html', vendors=vendors, total_mah=total_mah)

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
    logic.add_new_vendor(request.form['brand'], request.form['user'], request.form['pwd'])
    return redirect(url_for('admin_accounts'))

@app.route('/logout')
def logout():
    session.clear(); return redirect(url_for('login_admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
