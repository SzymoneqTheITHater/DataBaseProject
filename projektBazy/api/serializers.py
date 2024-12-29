from rest_framework import serializers
from shop.models import Category, Listing, Address
from django.contrib.auth.models import User
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    
class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model=User
        fields = ['id', 'username', 'email']    



class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'price', 'location', 'category', 'id']

    def create(self, validated_data):
        validated_data['seller'] = self.context['request'].user
        return super().create(validated_data)

class AdressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['country', 'town', 'street', 'postal_code', 'building_number', 'id']

    def create(self, validated_data):
        validated_data['resident'] = self.context['request'].user
        return super().create(validated_data) 

