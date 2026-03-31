from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db, Vendor, Product
import finance
import bridge_logic
import os

app = Flask(__name__)
app.config.from_object(Config)
init_db(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = Vendor.query.filter_by(username=request.form.get('username')).first()
        if not user:
            flash("المستخدم غير مسجل", "error")
        elif user.password != request.form.get('password'):
            flash("كلمة المرور خاطئة", "error")
        else:
            session['vendor_id'] = user.id
            return redirect(url_for('dashboard'))
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
    f_price = finance.calculate_final_price(request.form.get('price'))
    status = bridge_logic.push_to_store({"name": request.form.get('name'), "price": f_price})
    
    if status == "success":
        flash("تم الرفع والربط بنجاح!", "success")
    else:
        flash("فشل الاتصال بالمتجر الخارجي", "error")
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    with app.app_context(): db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
