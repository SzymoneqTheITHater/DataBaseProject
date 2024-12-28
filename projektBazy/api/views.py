from rest_framework.response import Response
from rest_framework.decorators import api_view
from shop.models import Category, Listing

from .serializers import CategorySerializer, ListingSerializer, UserSerializer
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
    return Response("passed for {}".format(request.user.username))