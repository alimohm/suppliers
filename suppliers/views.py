import requests
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# بيانات الربط من واجهة GraphQL الخاصة بمتجرك
GRAPHQL_URL = "https://mahjoub.online/admin/graphql"
# استبدل 'YOUR_TOKEN' بالمفتاح الظاهر في إعدادات قُمرة لديك
HEADERS = {"Authorization": "Bearer YOUR_TOKEN"}

@login_required
def dashboard(request):
    if request.method == 'POST':
        name = request.POST.get('product_name')
        supplier_price = float(request.POST.get('price'))
        
        # إضافة عمولة 40% تلقائياً
        final_price = supplier_price * 1.40
        
        # استعلام لإرسال المنتج كمسودة (Draft) إلى قُمرة
        mutation = """
        mutation createProduct($input: ProductInput!) {
          productCreate(input: $input) {
            product { id name }
          }
        }
        """
        variables = {
            "input": {
                "name": name,
                "basePrice": final_price,
                "status": "DRAFT",
                "description": f"مورد: {request.user.username}"
            }
        }
        
        try:
            requests.post(GRAPHQL_URL, json={'query': mutation, 'variables': variables}, headers=HEADERS)
            return render(request, 'success.html', {'final_price': final_price})
        except:
            return render(request, 'error.html')

    return render(request, 'dashboard.html')
