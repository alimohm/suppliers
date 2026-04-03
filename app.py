import os
from flask import Flask, render_template, request, redirect, url_for, session, flash

# 1. استيراد الإعدادات والمحرك وقاعدة البيانات
from config import Config
from database import db, init_db
from models import Vendor, AdminUser, Product, seed_admin

# 2. استيراد المنطق البرمجي المطور للبوابات
from logic import login_vendor, is_logged_in
from admin_logic import verify_admin_credentials, is_admin_logged_in

app = Flask(__name__)
app.config.from_object(Config)

# ربط التطبيق بقاعدة بيانات Postgres في Railway
init_db(app)

# 3. تهيئة النظام: بناء الجداول وحقن بيانات "علي محجوب" فور الإقلاع
with app.app_context():
    # سيقوم هذا السطر ببناء الجداول فور حذف القديمة لضمان وجود عمود status
    db.create_all() 
    # حقن بيانات الإدارة (علي محجوب / 123) والمورد الافتراضي
    seed_admin() 

# --- [ البوابات والروابط - Routes ] ---

@app.route('/')
def index():
    """التوجيه التلقائي حسب رتبة المستخدم المتصل"""
    if is_admin_logged_in():
        return redirect(url_for('admin_dashboard'))
    if is_logged_in():
        return redirect(url_for('vendor_dashboard'))
    return redirect(url_for('login_page'))

# --- [ بوابة دخول الموردين ] ---
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if is_logged_in():
        return redirect(url_for('vendor_dashboard'))
    
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        
        # تنفيذ منطق الدخول المطور (الذي يفرق بين عدم التسجيل وخطأ الب
