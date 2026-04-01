from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import init_db
import logic

app = Flask(__name__)
init_db(app) # تهيئة القاعدة فوراً

@app.route('/login', methods=['GET', 'POST'])
def lv():
    if request.method == 'POST':
        # طلب التحقق من ملف المنطق
        res = logic.do_auth(request.form.get('username'), request.form.get('password'))
        
        if res['status']:
            # تخزين البيانات للهيكل الثابت
            session.update({
                'v_id': res['user'].id,
                'owner_name': res['user'].owner_name,
                'brand_name': res['user'].brand_name or "محجوب أونلاين"
            })
            return redirect(url_for('db_v'))
        
        flash(res['msg'], "error")
    return render_template('login.html')
