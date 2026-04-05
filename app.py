import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import Config
from database import db, init_db
import models
from admin_logic import verify_admin_credentials, get_admin_stats, approve_vendor_logic, get_dashboard_data

app = Flask(__name__)
app.config.from_object(Config)
init_db(app)

with app.app_context():
    db.create_all()
    models.seed_initial_data()

@app.route('/')
def index():
    if session.get('role') == 'super_admin': return redirect(url_for('admin_dashboard'))
    return redirect(url_for('admin_login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        u, p = request.form.get('username'), request.form.get('password')
        ok, msg = verify_admin_credentials(u, p)
        if ok:
            session['username'], session['role'] = u, 'super_admin'
            return redirect(url_for('admin_dashboard'))
        flash(msg, "danger")
    return render_template('login_admin.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'super_admin': return redirect(url_for('admin_login'))
    return render_template('admin_main.html', username=session.get('username'), stats=get_admin_stats())

@app.route('/admin/vendors-accreditation')
def vendors_accreditation():
    if session.get('role') != 'super_admin': return redirect(url_for('admin_login'))
    return render_template('admin_accounts.html', vendors=get_dashboard_data(), pending_count=get_admin_stats()['pending'], username=session.get('username'))

@app.route('/admin/approve/<int:vendor_id>', methods=['POST'])
def approve_vendor(vendor_id):
    approve_vendor_logic(vendor_id)
    return redirect(url_for('vendors_accreditation'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
