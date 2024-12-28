from django.contrib import admin
from .models import User, Listing, Address, Category

# Register your models here.
admin.site.register(Listing)
admin.site.register(Address)
admin.site.register(Category)