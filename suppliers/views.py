import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

URL = "https://mahjoub.online/admin/graphql"
# ضع الـ Token الذي ستنشئه من قمرة هنا
HEADERS = {"Authorization": "Bearer YOUR_ACCESS_TOKEN"}

@login_required
def dashboard(request):
    if request.method == 'POST':
        p_name = request.POST.get('product_name')
        p_price = float(request.POST.get('price'))
        
        # إضافة 40% آلياً
        final_price = p_price * 1.40 
        
        mutation = """
        mutation { productCreate(input: { name: "%s", basePrice: %f, status: DRAFT }) { product { id } } }
        """ % (p_name, final_price)
        
        try:
            requests.post(URL, json={'query': mutation}, headers=HEADERS)
            return render(request, 'success.html', {'final_price': final_price})
        except:
            return render(request, 'error.html')

    return render(request, 'dashboard.html')
