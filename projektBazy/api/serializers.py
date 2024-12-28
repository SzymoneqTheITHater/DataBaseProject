from rest_framework import serializers
from shop.models import Category, Listing
from django.contrib.auth.models import User
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = '__all__'

    
class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model=User
        fields = ['id', 'username', 'email']    

