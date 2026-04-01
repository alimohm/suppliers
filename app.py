import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import init_db
import logic

app = Flask(__name__)
# تهيئة قاعدة البيانات من ملفها المستقل لمنع التكرار
init_db(app)

@app.route('/')
def index():
    return redirect(url_for('lv'))

@app.route('/login', methods=['GET', 'POST'])
def lv():
    if 'v_id' in session: return redirect(url_for('db_v'))
    
    if request.method == 'POST':
        # تمرير الطلب مباشرة للمنطق دون تخزين وسيط لتقليل استهلاك الرام
        res = logic.do_auth(request.form.get('username'), request.form.get('password'))
        if res['status']:
            session.update({'v_id': res['user'].id, 'name': res['user'].owner_name})
            return redirect(url_for('db_v'))
        flash(res['msg'], "error")
        
    return render_template('login.html')

@app.route('/dashboard')
def db_v():
    if 'v_id' not in session: return redirect(url_for('lv'))
    return f"مرحباً {session.get('name')}"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
