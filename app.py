from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import init_db
import logic # استيراد العقل المنفصل

app = Flask(__name__)
init_db(app) # تهيئة القاعدة فور التشغيل

@app.route('/login', methods=['GET', 'POST'])
def lv():
    if request.method == 'POST':
        # إرسال البيانات للمنطق
        res = logic.do_auth(request.form.get('username'), request.form.get('password'))
        
        if res['status']:
            session['v_id'] = res['user'].id
            return redirect(url_for('db_v'))
        
        # ظهور الرسالة المخصصة في الواجهة
        flash(res['msg'], "error")
        
    return render_template('login.html')
