from django.urls import path, include
from . import views




urlpatterns = [
    
    path('', views.store , name='store'),
    path('category/<slug:category_slug>/',views.store, name='product_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/',views.product_detail, name='product_detail'),
    path('search/', views.search , name='search'),
    path('submit_review/<int:product_id>/', views.submitReview , name='submit_review'),

]