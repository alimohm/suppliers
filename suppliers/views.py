import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

URL = "https://mahjoub.online/admin/graphql"
HEADERS = {"Authorization": "Bearer YOUR_ACCESS_TOKEN"} # ضع التوكن هنا

@login_required
def dashboard(request):
    if request.method == 'POST':
        p_name = request.POST.get('product_name')
        p_price = float(request.POST.get('price'))
        final_price = p_price * 1.40 # إضافة 40%
        
        mutation = """
        mutation { productCreate(input: { name: "%s", basePrice: %f, status: DRAFT }) { product { id } } }
        """ % (p_name, final_price)
        
        try:
            requests.post(URL, json={'query': mutation}, headers=HEADERS)
            return render(request, 'success.html', {'final_price': final_price})
        except:
            return render(request, 'error.html')
            
    return render(request, 'dashboard.html')
