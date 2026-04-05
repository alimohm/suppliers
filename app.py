import os, random
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db
import models, finance_logic, product_logic, vendor_logic, admin_logic

app = Flask(__name__)
app.config.from_object(Config)
init_db(app)

with app.app_context():
    db.create_all()
    models.seed_initial_data()

@app.route('/')
def index():
    if session.get('role') == 'super_admin': return redirect(url_for('admin_dashboard'))
    return redirect(url_for('vendor_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'super_admin': return redirect(url_for('admin_login'))
    v_count = models.Vendor.query.count()
    total_mah = db.session.query(db.func.sum(models.Wallet.balance)).scalar() or 0
    return render_template('admin_dashboard.html', vendors_count=v_count, total_mah=total_mah)

@app.route('/admin/add-vendor', methods=['POST'])
def admin_add_vendor_post():
    new_v = models.Vendor(brand_name=request.form['brand_name'], username=request.form['username'], password=request.form['password'])
    db.session.add(new_v); db.session.flush()
    wallet_no = f"MAH-{random.randint(100000, 999999)}"
    db.session.add(models.Wallet(wallet_number=wallet_no, vendor_id=new_v.id, balance=0))
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/vendor/dashboard')
def vendor_dashboard():
    v_id = session.get('vendor_id')
    wallet = models.Wallet.query.filter_by(vendor_id=v_id).first()
    products = models.Product.query.filter_by(vendor_id=v_id).all()
    return render_template('vendor_dashboard.html', wallet=wallet, products=products)

@app.route('/vendor/add-product', methods=['POST'])
def vendor_add_product_post():
    product_logic.add_new_product(session['vendor_id'], request.form['name'], request.form['price'], request.form['stock'], request.files.get('image'))
    return redirect(url_for('vendor_dashboard'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
