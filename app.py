import os, random
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db, User, Wallet, Product
import logic

app = Flask(__name__)
app.config.from_object(Config)
init_db(app)

@app.route('/')
def index():
    if 'user_id' not in session: return redirect(url_for('login'))
    return redirect(url_for('admin_dashboard' if session['role'] == 'admin' else 'vendor_dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form['username'], request.form['password']
        user = User.query.filter_by(username=u, password=p).first()
        if user:
            session.update({'user_id': user.id, 'username': u, 'role': user.role})
            return redirect(url_for('index'))
        # التصحيح هنا: استخدام الفاصلة الإنجليزية , 
        flash("بيانات الدخول غير صحيحة", "danger")
    return render_template('login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    vendors = User.query.filter_by(role='vendor').all()
    total_mah = db.session.query(db.func.sum(Wallet.balance)).scalar() or 0
    return render_template('admin_dashboard.html', vendors=vendors, total_mah=total_mah)

@app.route('/vendor/dashboard')
def vendor_dashboard():
    if session.get('role') != 'vendor': return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('vendor_dashboard.html', wallet=user.wallet, products=user.products)

@app.route('/action/add-vendor', methods=['POST'])
def add_vendor():
    logic.add_new_vendor(request.form['brand'], request.form['user'], request.form['pwd'])
    return redirect(url_for('admin_dashboard'))

@app.route('/action/transfer', methods=['POST'])
def transfer():
    success, msg = logic.execute_transfer(session['user_id'], request.form['target'], float(request.form['amount']), request.form['note'])
    flash(msg, "success" if success else "danger")
    return redirect(url_for('vendor_dashboard'))

@app.route('/action/add-product', methods=['POST'])
def add_product():
    logic.add_vendor_product(session['user_id'], request.form['name'], request.form['price'], request.form['stock'], request.files.get('image'), app.config['UPLOAD_FOLDER'])
    return redirect(url_for('vendor_dashboard'))

@app.route('/logout')
def logout():
    session.clear(); return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
