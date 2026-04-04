import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db

app = Flask(__name__)
app.config.from_object(Config)
init_db(app)

# --- [ منطقة السيادة وإعادة الهيكلة ] ---
with app.app_context():
    import models
    # الحل النهائي: سيتم مسح الجداول القديمة وبناء الجديدة بالأعمدة المطلوبة
    try:
        db.drop_all() 
        db.create_all() 
        models.seed_system()
        print("✅ تم تطهير قاعدة البيانات وحقن بيانات 'علي محجوب' بنجاح.")
    except Exception as e:
        print(f"❌ خطأ في تهيئة القاعدة: {e}")

# --- [ المسارات: Routes ] ---

@app.route('/')
def index():
    return redirect(url_for('vendor_login'))

@app.route('/vendor/login', methods=['GET', 'POST'])
def vendor_login():
    if request.method == 'POST':
        from vendor_logic import login_vendor
        u = request.form.get('username', '').strip()
        p = request.form.get('password', '').strip()
        success, msg = login_vendor(u, p)
        if success:
            return redirect(url_for('vendor_dashboard'))
        flash(msg, "danger")
    return render_template('vendor_login.html')

@app.route('/vendor/dashboard')
def vendor_dashboard():
    if 'role' not in session:
        return redirect(url_for('vendor_login'))
    # المالك يرى المحفظة، الموظف لا يراها
    show_wallet = (session.get('role') == 'vendor_owner')
    return render_template('dashboard.html', username=session.get('username'), show_wallet=show_wallet)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('vendor_login'))

if __name__ == '__main__':
    # التوافق مع بورت Railway المتغير
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
