from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from shop.models import Category, Listing, Address, Transaction
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import CategorySerializer, ListingSerializer, UserSerializer, AdressSerializer, TransactionSerializer
from rest_framework import status, generics
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotFound
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema


@api_view(['GET'])
def getCategory(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    
    
    return Response(serializer.data)
@swagger_auto_schema(methods=['get'], responses={200: ListingSerializer(many=True)})
@api_view(['GET'])
def getData(request):
    listings = Listing.objects.all()
    serializer = ListingSerializer(listings, many=True)
    
    
    return Response(serializer.data)
#also unnessesary, user shouldnt be able to add categories, its just for testing 
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
#i dont think i understand to good swagger yet :()
@swagger_auto_schema(methods=['post'], request_body=ListingSerializer, responses={201: ListingSerializer})
@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def post_listing(request):
    serializer=ListingSerializer(data=request.data,  context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
class CreateListingView(generics.CreateAPIView):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticated]
    def perform_create(self, serializer):
        serializer.save()

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_address(request):
    serializer=AdressSerializer(data=request.data,  context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListingsView(generics.ListAPIView):
    serializer_class = ListingSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user_id') 
        category_id = self.kwargs.get('category_id')

        if user_id and not category_id:        
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise NotFound("User not found")

            return Listing.objects.filter(seller=user)
        if category_id and not user_id:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                raise NotFound("Category not found")
            category.number_of_items = Listing.objects.filter(category=category).count()
            category.save()
            return Listing.objects.filter(category=category)
        if user_id and category_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise NotFound("User not found")
            
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                raise NotFound("Category not found")
            
            return Listing.objects.filter(seller=user, category=category)
    

class UserAddressesView(generics.ListAPIView):
    serializer_class = AdressSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound("User not found")

        return Address.objects.filter(resident=user)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_transaction(request):
    if request.method == 'POST':

        listing_id = request.data.get('listing')

        try:
            listing = Listing.objects.get(id=listing_id)
        except Listing.DoesNotExist:
            return Response({'detail': 'Listing not found'}, status=status.HTTP_404_NOT_FOUND)

        if listing.seller == request.user:
            return Response({'detail': 'You cannot buy your own listing'}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            'listing': listing_id,
        }

        serializer = TransactionSerializer(data=data, context={'request': request})

        if serializer.is_valid():
            transaction = serializer.save(seller=listing.seller)
            return Response(TransactionSerializer(transaction).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

#before i forget, patch only sends the data that is changed, so the objcet must be created before, i think you can create with put.
@api_view(['PATCH'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_transaction_status(request, transaction_id):
    try:
        transaction = Transaction.objects.get(id=transaction_id)
    except Transaction.DoesNotExist:
        return Response({'detail': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.user == transaction.seller:
        allowed_status = [Transaction.PENDING, Transaction.COMPLETED, Transaction.CANCELLED]  
    else:
        return Response({'detail': 'You do not have permission to update this transaction.'}, status=status.HTTP_403_FORBIDDEN)

    new_status = request.data.get('status')
    if new_status not in dict(Transaction.STATUS_CHOICES).keys():
        return Response({'detail': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)
    
    
    if new_status not in allowed_status:
        return Response({'detail': 'You cannot change the status to this value.'}, status=status.HTTP_400_BAD_REQUEST)

    transaction.status = new_status
    if new_status == Transaction.COMPLETED:
        transaction.listing.state = Listing.BOUGHT  
    elif new_status == Transaction.CANCELLED:
        transaction.listing.state = Listing.ACTIVE  
    elif new_status == Transaction.PENDING:
        transaction.listing.state = Listing.PENDING



    transaction.save()
    transaction.listing.save()

    return Response(TransactionSerializer(transaction).data, status=status.HTTP_200_OK)

@api_view(['PATCH'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def cancel_listing(request, listing_id):
    try:
        listing = Listing.objects.get(id=listing_id)
    except Listing.DoesNotExist:
        return Response({'detail': 'Listing not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.user != listing.seller:
        return Response({'detail': 'You do not have permission to cancel this listing.'}, status=status.HTTP_403_FORBIDDEN)

    if listing.state != Listing.ACTIVE:
        return Response({'detail': 'This listing cannot be cancelled because it is not active.'}, status=status.HTTP_400_BAD_REQUEST)

    listing.state = Listing.CANCELLED
    listing.save()

    serializer = ListingSerializer(listing)
    return Response(serializer.data, status=status.HTTP_200_OK)

    

    
    