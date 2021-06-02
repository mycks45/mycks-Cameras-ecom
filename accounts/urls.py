from django.urls import path, include, re_path

from . import views






urlpatterns = [
    
    path('register/', views.register , name='register'),
    path('user_login/', views.userLogin , name='user_login'),
    path('user_logout/', views.userLogout , name='user_logout'),

    path('referral/', views.referral , name='referral'),

    path('profile/', views.profile , name='profile'),
    path('add_address/', views.addAddress , name='add_address'),
    path('address_delete/<int:id>/', views.addressDelete , name='address_delete'),
    path('address_update/<int:id>/', views.addressUpdate , name='address_update'),
    path('edit_profile/', views.editProfile , name='edit_profile'),
    path('change_password/', views.changePassword , name='change_password'),

    path('my_order/', views.myOrder , name='my_order'),
    path('my_order_history/', views.myOrderHistory , name='my_order_history'),
    path('user_order_details/<int:order_id>/', views.userOrderDetails , name='user_order_details'),
    path('user_delete_order/<int:id>/', views.userdeleteOrder , name='user_delete_order'),

    path('forgot_password/', views.forgotPassword , name='forgot_password'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate , name='resetpassword_validate'),
    path('reset_password/', views.resetPassword , name='reset_password'),

    path('sign_in_otp/', views.sign_in_otp , name='sign_in_otp'),
    path('OTP_page/', views.OTP_page , name='OTP_page'),
    
]
