from rest_framework import serializers
from shop.models import Category, Listing, Address, Transaction, Message, Chat
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
        fields = ['title', 'description', 'price', 'location','created_at', 'category', 'id']

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

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['listing', 'seller', 'buyer', 'transaction_date', 'status']
        read_only_fields = ['seller', 'buyer', 'transaction_date']  
    
    def create(self, validated_data):
        
        listing = validated_data['listing']
        buyer = self.context['request'].user  
        
        
        seller = listing.seller
        
        
        transaction = Transaction.objects.create(
            listing=listing,
            seller=seller,
            buyer=buyer
        )
        return transaction

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = ['buyer', 'seller', 'listing']
        read_only_fields = ['buyer', 'seller', 'listing']
    
    def create(self, validated_data):
        buyer = self.context['request'].user  
        seller = validated_data['seller']
        listing = validated_data['listing']
        
        chat = Chat.objects.create(
            buyer=buyer,
            seller=seller,
            listing=listing
        )   
        return chat


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['chat', 'sender', 'content', 'status', 'created_at', 'viewed_at']
        read_only_fields = ['chat', 'sender', 'status', 'created_at', 'viewed_at']
    
    def create(self, validated_data):
        chat = validated_data['chat']
        content = validated_data['content']
        sender = self.context['request'].user  
        message = Message.objects.create(
            chat=chat,
            content=content,
            sender=sender
        )   
        return message

