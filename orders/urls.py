from django.urls import path, include
from . import views




urlpatterns = [
    
    path('place_order/', views.placeOrder , name='place_order'),
    path('payments/', views.payments , name='payments'),
    path('paypal/', views.paypal , name='paypal'),
    path('razorpay/', views.razorpay , name='razorpay'),
    path('order_complete/', views.orderComplete , name='order_complete'),
    path('address_choice/<int:id>/', views.addressChoice , name='address_choice'),
    
]
