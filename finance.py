def calculate_final_price(cost, currency="USD"):
    """منطق زيادة الـ 30% الملكية"""
    try:
        price = float(cost)
        return round(price * 1.30, 2)
    except:
        return 0.0
