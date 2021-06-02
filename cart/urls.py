from django.urls import path
from . import views


urlpatterns = [
    path('', views.cart, name='cart'),
    path('add_cart/<int:product_id>/', views.addCart, name='add_cart'),
    path('remove_cart/<int:product_id>/', views.removeCart, name='remove_cart'),
    path('remove_cart_items/<int:product_id>/', views.removeCartItems, name='remove_cart_items'),
    
    path('checkout/', views.checkout, name='checkout'),
    path('ajax-posting/', views.ajax_posting, name='ajax_posting'),# ajax-posting / name = that we will use in ajax url
    path('ajax-postingPlus/', views.ajax_postingPlus, name='ajax_postingPlus'),# ajax-posting / name = that we will use in ajax url

   

]

