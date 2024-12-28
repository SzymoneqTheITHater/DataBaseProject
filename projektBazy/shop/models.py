from django.db import models
from django.contrib.auth.models import User  

class Listing(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.FloatField()
    location = models.CharField(max_length=255)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings', to_field='id')  
    isActive = models.BooleanField(default=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='listings')
    def __str__(self):
        return self.title

class Category(models.Model):
    category_name=models.CharField(max_length=63)
    number_of_items=models.IntegerField()

    
    def update_number_of_items(self):
        self.number_of_items = self.listings.count()
        self.save()
    def __str__(self):
        return (f"{self.category_name}, total:{self.number_of_items}")

class Address(models.Model):
    country = models.CharField(max_length=63)
    town = models.CharField(max_length=63)
    street = models.CharField(max_length=63)
    postal_code = models.IntegerField()
    building_number = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')   

    def __str__(self):
        return f"street and number: {self.building_number} {self.street}, city: {self.town}, country: {self.country}"
    