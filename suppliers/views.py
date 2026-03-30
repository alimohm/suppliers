import requests
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# بيانات الربط من واجهة GraphQL الخاصة بك
GRAPHQL_URL = "https://mahjoub.online/admin/graphql"
# تأكد من وضع الـ Token الصحيح هنا
HEADERS = {"Authorization": "Bearer YOUR_QUMRA_ACCESS_TOKEN"}

@login_required
def dashboard(request):
    if request.method == 'POST':
        product_name = request.POST.get('name')
        supplier_price = float(request.POST.get('price'))
        
        # إضافة عمولة 40% تلقائياً للمتجر
        market_price = supplier_price * 1.40
        
        # استعلام GraphQL لإرسال المنتج كمسودة
        mutation = """
        mutation createProduct($input: ProductInput!) {
          productCreate(input: $input) {
            product { id name }
          }
        }
        """
        variables = {
            "input": {
                "name": product_name,
                "basePrice": market_price,
                "status": "DRAFT",
                "description": f"توريد بواسطة المورد: {request.user.username}"
            }
        }
        
        try:
            requests.post(GRAPHQL_URL, json={'query': mutation, 'variables': variables}, headers=HEADERS)
            return render(request, 'success.html', {'final_price': market_price})
        except:
            return render(request, 'error.html')

    return render(request, 'dashboard.html')
