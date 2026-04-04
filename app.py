import os
from flask import Flask, session
from config import Config
from database import db, init_db

app = Flask(__name__)
app.config.from_object(Config)

# 1. تهيئة القاعدة
init_db(app)

# 2. إنشاء الجداول وحقن البيانات (الحل النهائي للخطأ)
with app.app_context():
    # استيراد الموديلات داخل السياق يمنع الدوران العكسي
    import models 
    db.create_all() 
    models.seed_system()

# 3. استيراد المنطق (Logic) بعد تهيئة التطبيق
# تأكد أن الملفات موجودة في مجلد المشروع كما في صورتك
from vendor_logic import login_vendor, is_logged_in
from admin_logic import verify_admin_credentials

# --- [ هنا تضع الـ Routes (المسارات) ] ---
@app.route('/')
def index():
    return "منصة محجوب أونلاين جاهزة للعمل بنجاح يا عظيم!"

if __name__ == '__main__':
    app.run(debug=True, port=8080)
