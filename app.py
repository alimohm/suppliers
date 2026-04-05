import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import db, init_system, Vendor, Wallet, Product, Transaction, SuperAdmin
import logic

app = Flask(__name__)
app.config['SECRET_KEY'] = 'MAHJOUB_2026_KEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mahjoub.db'

init_system(app)

@app.route('/')
def home():
    if 'role' in session:
        return redirect(url_for('admin_dashboard' if session['role']=='admin' else 'vendor_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form['username'], request.form['password']
        admin = SuperAdmin.query.filter_by(username=u, password=p).first()
        if admin:
            session.update({'role': 'admin', 'username': u})
            return redirect(url_for('admin_dashboard'))
        v = Vendor.query.filter_by(username=u, password=p).first()
        if v:
            session.update({'role': 'vendor', 'vendor_id': v.id, 'username': u})
            return redirect(url_for('vendor_dashboard'))
        flash("خطأ في البيانات", "danger")
    return render_template('login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin': return redirect(url_for('login'))
    return render_template('admin_dashboard.html', vendors=Vendor.query.all())

@app.route('/vendor/dashboard')
def vendor_dashboard():
    if session.get('role') != 'vendor': return redirect(url_for('login'))
    v_id = session['vendor_id']
    return render_template('vendor_dashboard.html', 
                           wallet=Wallet.query.filter_by(vendor_id=v_id).first(),
                           products=Product.query.filter_by(vendor_id=v_id).all())

@app.route('/action/add-vendor', methods=['POST'])
def add_vendor():
    logic.add_vendor_with_wallet(request.form['brand'], request.form['user'], request.form['pwd'])
    return redirect(url_for('admin_dashboard'))

@app.route('/action/transfer', methods=['POST'])
def transfer():
    v_id = session['vendor_id']
    w = Wallet.query.filter_by(vendor_id=v_id).first()
    logic.process_transfer(w.id, request.form['target'], float(request.form['amount']), request.form['note'])
    return redirect(url_for('vendor_dashboard'))

@app.route('/action/add-product', methods=['POST'])
def add_product():
    logic.save_product(session['vendor_id'], request.form['name'], request.form['price'], request.form['stock'], request.files.get('image'))
    return redirect(url_for('vendor_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
