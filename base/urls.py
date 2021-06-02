from django.urls import path, include
from . import views




urlpatterns = [
    
    path('', views.home , name='home'),
    path('contact_us/', views.contactUs , name='contact_us'),
    

]
