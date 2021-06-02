from django.urls import path, include
from . import views




urlpatterns = [
    
    path('', views.adminPanel , name='admin_panel'),
    path('login_admin/', views.loginAdmin , name='login_admin'),
    path('logout_admin/', views.logoutAdmin, name='logout_admin'),
    
    path('user_mgt/', views.userMgt , name='user_mgt'),
    path('block_user/<str:pk>/', views.blockUser, name='block_user'),
    path('referrence_stats/<str:pk>/', views.referrenceStats, name='referrence_stats'),
    path('delete_user/<str:pk>/', views.deleteUser, name='delete_user'),
    
    path('category_mgt/', views.categoryMgt , name='category_mgt'),
    path('add_category/', views.addCategory , name='add_category'),
    
    path('product_mgt/', views.productMgt , name='product_mgt'),
    path('add_product/', views.addProduct , name='add_product'),
    path('delete_product/<int:id>/', views.deleteProduct , name='delete_product'),
    path('update_product/<int:id>/', views.updateProduct , name='update_product'),
    
    path('order_mgt/', views.orderMgt, name='order_mgt'),
    path('delete_order/<int:id>/', views.deleteOrder , name='delete_order'),
    path('order_detail/<int:id>/', views.orderDetail , name='order_detail'),
    
    path('coupons_mgt/', views.couponsMgt, name='coupons_mgt'),
    path('coupons_add/', views.couponsAdd, name='coupons_add'),
    path('delete_coupon/<int:id>/', views.deleteCoupon , name='delete_coupon'),
    path('coupon_status/<int:id>/', views.couponStatus , name='coupon_status'),

    path('admin_Search/', views.adminSearch, name='admin_Search'),
    path('sales_report/', views.sales_report, name='sales_report'),
    
    

]
