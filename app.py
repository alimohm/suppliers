import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import db, init_db
import logic # استدعاء العقل المنفصل لتقليل استهلاك الذاكرة

app = Flask(__name__)
app.secret_key = os.environ.get("SK", "M_26_R") # مفتاح مختصر لتقليل الحجم
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # تحسين أداء الذاكرة

init_db(app)

@app.route('/')
def index():
    return redirect(url_for('lv')) # lv اختصار لـ Login View

@app.route('/login', methods=['GET', 'POST'])
def lv():
    if 'v_id' in session: return redirect(url_for('db_v')) # db_v للـ Dashboard
    
    if request.method == 'POST':
        # استخدام دوال المنطق مباشرة لتقليل أسطر الكود في الملف الرئيسي
        res = logic.do_auth(request.form.get('u'), request.form.get('p'))
        if res['status']:
            session.update({'v_id': res['user'].id, 'name': res['user'].owner_name})
            return redirect(url_for('db_v'))
        flash(res['message'], "e")
        
    return render_template('login.html')

@app.route('/dashboard')
def db_v():
    if 'v_id' not in session: return redirect(url_for('lv'))
    return render_template('dashboard.html', name=session.get('name'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
