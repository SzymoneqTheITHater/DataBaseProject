from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import Listing
from .forms import ListingForm
from django.contrib.auth.models import User  


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  
        
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

#how logging looks like, it will need to be changed in the future (few days) to some api mumbojumbo but its easier for now like this i think
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  
        else:
            return render(request, 'login.html', {'error': 'Invalid login credentials'})
    return render(request, 'login.html')

#random comment to test git
def user_logout(request):
    logout(request)
    return redirect('home')  

@login_required
def create_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            #listing.seller = request.user.id  
            listing.seller=User.objects.get(id=request.user.id)
            listing.save()
            #return redirect('listing_detail', pk=listing.pk)  
            return redirect('home')
    else:
        form = ListingForm()
    return render(request, 'create_listing.html', {'form': form})

# Simple listing view
def listing_list(request):
    listings = Listing.objects.filter(isActive=True)  
    return render(request, 'listing_list.html', {'listings': listings})
