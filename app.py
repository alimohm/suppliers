import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import db, init_db
import models
from admin_logic import get_admin_stats, get_dashboard_data, approve_vendor_logic

app = Flask(__name__)
app.secret_key = "mahjoub_secret_key" # مفتاح الأمان
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///mahjoub.db")

init_db(app)

@app.before_first_request
def setup():
    db.create_all()
    models.seed_initial_data()

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    stats = get_admin_stats()
    return render_template('admin_main.html', username=session.get('username'), stats=stats)

@app.route('/admin/vendors-accreditation')
def vendors_accreditation():
    if session.get('role') != 'super_admin':
        return redirect(url_for('admin_login'))
    
    all_vendors = get_dashboard_data()
    stats = get_admin_stats()
    
    # الربط السيادي: نرسل البيانات لملف admin_accounts.html
    return render_template('admin_accounts.html', 
                           username=session.get('username'),
                           vendors=all_vendors, 
                           pending_count=stats.get('pending', 0))

@app.route('/admin/approve/<int:vendor_id>', methods=['POST'])
def approve_vendor(vendor_id):
    success, msg = approve_vendor_logic(vendor_id)
    flash(msg, "success" if success else "danger")
    return redirect(url_for('vendors_accreditation'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
