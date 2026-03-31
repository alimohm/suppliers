import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import db, init_db, Vendor
import logic, finance, bridge_logic
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
init_db(app)

@app.route('/')
def index():
    return redirect(url_for('dashboard')) if 'vendor_id' in session else redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form.get('username'), request.form.get('password')
        vendor, msg = logic.perform_login(u, p)
        if vendor:
            session['vendor_id'] = vendor.id
            return redirect(url_for('dashboard'))
        flash(msg)
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    v_id = session.get('vendor_id')
    if not v_id: return redirect(url_for('login'))
    vendor = Vendor.query.get(v_id)
    return render_template('dashboard.html', vendor=vendor)

@app.route('/add_product', methods=['POST'])
def add_product():
    v_id = session.get('vendor_id')
    if not v_id: return redirect(url_for('login'))
    
    vendor = Vendor.query.get(v_id)
    final_price = finance.calculate_final_price(request.form.get('price'), request.form.get('currency'))
    
    data = {
        "name": request.form.get('name'),
        "final_price": final_price,
        "description": request.form.get('description'),
        "wallet": vendor.wallet_address
    }
    
    if bridge_logic.push_to_store(data):
        flash(f"تم النشر كمسودة! السعر النهائي بعد زيادة 30%: {final_price} ر.س")
    else:
        flash("فشل الربط مع متجر محجوب أونلاين.")
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
