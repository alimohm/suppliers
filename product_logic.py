import os
from werkzeug.utils import secure_filename
from models import Product
from database import db

def add_new_product(vendor_id, name, price, stock, file):
    image_url = '/static/images/default.png'
    if file:
        filename = secure_filename(f"v{vendor_id}_{file.filename}")
        os.makedirs('static/uploads', exist_app=True)
        file.save(os.path.join('static/uploads', filename))
        image_url = f'/static/uploads/{filename}'
    
    new_p = Product(vendor_id=vendor_id, name=name, price=float(price), stock=int(stock), image_url=image_url)
    db.session.add(new_p)
    db.session.commit()
    return True, "تمت الإضافة"
