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
    created_at = models.DateTimeField(auto_now_add=True)
    
    #actually i dont think i need this anymore, but lets leave it for now (leftover from forms->api switch)
    def __str__(self):
        return self.title

class Category(models.Model):
    category_name=models.CharField(max_length=63)
    number_of_items=models.IntegerField()

    
    
    def __str__(self):
        return (f"{self.category_name}, total:{self.number_of_items}")

class Address(models.Model):
    country = models.CharField(max_length=63)
    town = models.CharField(max_length=63)
    street = models.CharField(max_length=63)
    postal_code = models.IntegerField()
    building_number = models.IntegerField()
    resident = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='addresses')   
    

    def __str__(self):
        return f"street and number: {self.building_number} {self.street}, city: {self.town}, country: {self.country}"
    


class Transaction(models.Model):
    PENDING = 'pending'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='transactions')  
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions_selling')  
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions_buying')  
    transaction_date = models.DateTimeField(auto_now_add=True)  
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)

    def save(self, *args, **kwargs):

        if not self.seller:
            self.seller = self.listing.seller
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Transaction between {self.seller.username} and {self.buyer.username} for {self.listing.title} curently {self.status}"

    