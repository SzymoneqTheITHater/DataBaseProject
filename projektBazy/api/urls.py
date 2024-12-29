from django.urls import path
from .views import ListingsView
from . import views
urlpatterns = [
    path('',views.getData),
    path('categories/',views.getCategory),
    path('add/', views.addCategory),
    path('login/', views.login),
    path('signup/', views.signup),
    path('test_token/', views.test_token),
    path('logout/', views.logout),
    path('postListing/', views.post_listing),
    path('postAddress/', views.add_address),
    #/listings/user/1/category/2/
    path('listings/user/<int:user_id>/category/<int:category_id>/', ListingsView.as_view(), name='user-category-listings'),
    #/listings/user/1/ np
    path('listings/user/<int:user_id>/', ListingsView.as_view(), name='user-listings'),    #/listings/category/2/
    path('listings/category/<int:category_id>/', ListingsView.as_view(), name='category-listings'),

]
#Do something like this to test it
#http://127.0.0.1:8000/postAddress/
#and for example put something like this: 
#   {
#       "country": "Poland",
#       "town": "Wrocław",
#       "street": "Świdnicka",
#       "postal_code": 50029,
#       "building_number": 15,
#       "id": 1
#   }