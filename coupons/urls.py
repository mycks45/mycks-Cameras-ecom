from django.urls import path
from . import views


urlpatterns = [
    
    path('coupon_apply/', views.coupon_apply, name='coupon_apply'),
    path('add_category_offer/', views.add_category_offer, name='add_category_offer'),
    path('activate_cat_offer/<str:cat_id>/', views.activate_cat_offer, name='activate_cat_offer'),
    path('delete_category_offer/<str:cat_id>/', views.delete_category_offer, name='delete_category_offer'),

]

