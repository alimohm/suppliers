from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import init_db
import logic # استيراد العقل المنفصل

app = Flask(__name__)
init_db(app) # تهيئة القاعدة فور التشغيل

@app.route('/login', methods=['GET', 'POST'])
def lv():
    if 'v_id' in session: return redirect(url_for('db_v'))
    
    if request.method == 'POST':
        res = logic.do_auth(request.form.get('username'), request.form.get('password'))
        if res['status']:
            # تخزين الهوية الملكية في الجلسة
            session.update({
                'v_id': res['user'].id,
                'owner_name': res['user'].owner_name,
                'brand_name': res['user'].brand_name or "متجر سيادي",
                'brand_logo_url': res['user'].brand_logo_url
            })
            return redirect(url_for('db_v'))
        flash(res['msg'], "error")
        
    return render_template('login.html')
