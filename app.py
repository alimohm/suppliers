import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import db, init_db
import logic
import bridge_logic 

app = Flask(__name__)
# مفتاح سري لتأمين جلسات الموردين
app.secret_key = os.environ.get('SECRET_KEY', 'mahjoub_king_2026_sovereign')

# تهيئة الاتصال بقاعدة بيانات ريلوي
init_db(app)

@app.route('/')
def index():
    if 'vendor_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        vendor_obj, message = logic.perform_login(u, p)
        if vendor_obj:
            session['vendor_id'] = vendor_obj.id
            return redirect(url_for('dashboard'))
        flash(message)
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    vendor_id = session.get('vendor_id')
    if not vendor_id:
        return redirect(url_for('login'))
    
    # جلب بيانات المورد الحالي
    vendor = logic.get_current_vendor(vendor_id)
    if not vendor:
        return redirect(url_for('login'))
        
    return render_template('dashboard.html', vendor=vendor)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
