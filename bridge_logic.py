import requests

def push_to_store(data):
    """التحقق من الاتصال بالويب هوك"""
    # هنا يتم وضع رابط الويب هوك الخاص بمتجرك
    try:
        # محاكاة نجاح الاتصال للتحقق
        return "success" 
    except:
        return "connection_error"
