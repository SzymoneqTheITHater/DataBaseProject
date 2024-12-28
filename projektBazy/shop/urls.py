from django.urls import path
from . import views

urlpatterns = [
    path('', views.listing_list, name='home'),  
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('create_listing/', views.create_listing, name='create_listing'),
   
]
