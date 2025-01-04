from django.contrib import admin
from .models import User, Listing, Address, Category, Transaction, Chat, Message, Review

# Register your models here.
admin.site.register(Listing)
admin.site.register(Address)
admin.site.register(Category)
admin.site.register(Transaction)
admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(Review)