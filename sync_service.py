import requests

# بيانات الربط مع قمرة
STORE_ID = "qmr_e235dd03-f398-473f-aa12-79029f05e147"
WEBHOOK_URL = f"https://api.qumra.cloud/v1/stores/{STORE_ID}/products"
API_KEY = "ضغ_المفتاح_هنا" 

def send_to_qumra_webhook(name, price, description):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "title": name,
        "price": float(price) if price else 0,
        "description": description,
        "metadata": {"origin": "Mahjoub Online"}
    }

    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers, timeout=10)
        return response.status_code in [200, 201]
    except:
        return False
