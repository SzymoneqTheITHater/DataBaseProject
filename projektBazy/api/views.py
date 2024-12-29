from rest_framework.response import Response
from rest_framework.decorators import api_view
from shop.models import Category, Listing, Address

from .serializers import CategorySerializer, ListingSerializer, UserSerializer, AdressSerializer
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404


@api_view(['GET'])
def getCategory(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    
    
    return Response(serializer.data)

@api_view(['GET'])
def getData(request):
    listings = Listing.objects.all()
    serializer = ListingSerializer(listings, many=True)
    
    
    return Response(serializer.data)

@api_view(['POST'])
def addCategory(request):

    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

@api_view(['POST'])
def signup(request):
    serializer=UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user=User.objects.get(username=request.data['username'])
        user.set_password(request.data['password'])
        user.save()
        token=Token.objects.create(user=user)
        return Response({"token": token.key, "user": serializer.data})
    return Response({serializer.errors})


@api_view(['POST'])
def login(request):
    user=get_object_or_404(User, username=request.data['username'])
    if not user.check_password(request.data['password']):
        return Response({"detalil":"Not found."})
    token, created= Token.objects.get_or_create(user=user)
    serializer=UserSerializer(instance=user)
    return Response({"token": token.key, "user": serializer.data})


from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response("22passed for {}".format(request.user.username))


# i mean the normal logging doesnt work here, but when you log as admin on /admin, you stay loged as admin and you pass token autorisation (probably writen it wrong) so it's good enough for now
#like you can use that loggin from above, and it is generating you token and stuff, but you aren't logged in???
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        request.user.auth_token.delete()
        return Response({"detail22": "Successfully logged out."}, status=200)
    except (AttributeError, Token.DoesNotExist):
        return Response({"detail22": "No active session or token found."}, status=400)
    
#To test those go login in http://127.0.0.1:8000/admin/   username osboxes password osboxes.org i think that the database and all paswords go through git??? not sure, if not create admin yourself. actually i dont think it goes to git but still, you can make a admin by yourself. 
#anyway, when you log as admin you can go back to the other urls and test all of those, and add more and stuff
@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def post_listing(request):
    serializer=ListingSerializer(data=request.data,  context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_address(request):
    serializer=AdressSerializer(data=request.data,  context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)