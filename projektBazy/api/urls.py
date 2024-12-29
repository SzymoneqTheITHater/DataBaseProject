from django.urls import path
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