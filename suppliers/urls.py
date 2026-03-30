from django.urls import path
from . import views

app_name = 'suppliers'

urlpatterns = [
    path('login/', views.supplier_login, name='login'),
    path('dashboard/', views.supplier_dashboard, name='dashboard'),
]
