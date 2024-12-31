from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from shop.models import Category, Listing, Address, Transaction, Message, Chat, Review
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import CategorySerializer, ListingSerializer, UserSerializer, AdressSerializer, TransactionSerializer, MessageSerializer, ChatSerializer, ReviewSerializer
from rest_framework import status, generics
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotFound
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from django.db.models import Avg
from datetime import datetime
#unnessesary
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

#needs work to stay loged in idk got lost in it 
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
        allowed_status = [Transaction.PENDING, Transaction.COMPLETED, Transaction.CANCELLED]  # Sprzedawca może zmieniać na "completed"
    else:
        return Response({'detail': 'You do not have permission to update this transaction.'}, status=status.HTTP_403_FORBIDDEN)

    new_status = request.data.get('status')
    if new_status not in dict(Transaction.STATUS_CHOICES).keys():
        return Response({'detail': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)
    
    
    if new_status not in allowed_status:
        return Response({'detail': 'You cannot change the status to this value.'}, status=status.HTTP_400_BAD_REQUEST)

    transaction.status = new_status
    transaction.save()

    return Response(TransactionSerializer(transaction).data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_chat_message(request, chat_id, listing_id):
    if request.method == 'POST':
        try:
            listing = Listing.objects.get(id=listing_id)
        except Listing.DoesNotExist:
            return Response({'detail': 'Listing not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            chat = Chat.objects.get(id=chat_id)
            if chat.listing_id != listing.id:
                return Response({'detail': 'Invalid chat for the listing'}, status=status.HTTP_400_BAD_REQUEST)
        
        except Chat.DoesNotExist:
            chat = None
                        
        if chat is None:
            
            if request.user.id == listing.seller.id:
                return Response({'detail': 'Seller can not start the chat'}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                newChat = {
                    'buyer': request.user,
                    'seller': listing.seller,
                    'listing': listing
                }
                chat_serializer = ChatSerializer(data=newChat, context={'request': request})
                if chat_serializer.is_valid():
                   chat = chat_serializer.save(seller=listing.seller, buyer=request.user, listing=listing)
            
            except Exception as e:
                return Response({'detail': 'Unable to create chat'}, status=status.HTTP_409_CONFLICT)

        new_message = {
            'content' : request.data.get('message')
        }

        message_serializer = MessageSerializer(data=new_message, context={'request': request})

        if message_serializer.is_valid():
            message_serializer.save(chat=chat)
            return Response(message_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(message_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_chats(request, listing_id):
    try:
        listing = Listing.objects.get(id=listing_id)
    except Listing.DoesNotExist:
        return Response({'detail': 'Listing not found'}, status=status.HTTP_404_NOT_FOUND)
    
    chats = Chat.objects.filter(listing=listing_id)
    serializer = ChatSerializer(chats, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_messages(request, chat_id):
    try:
        chat = Chat.objects.get(id=chat_id)
    except Chat.DoesNotExist:
        return Response({'detail': 'Chat not found'}, status=status.HTTP_404_NOT_FOUND)
    
    messages = Message.objects.filter(chat=chat)
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)

@api_view(['PATCH'])
def set_message_viewed(request, message_id):
    try:
        message = Message.objects.get(id=message_id)
        message.status = Message.Viewed
        message.viewed_at = datetime.now()
        message.save()
    except Message.DoesNotExist:
        return Response({'detail': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': 'Unable to update'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(MessageSerializer(message).data)    

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def create(self, request, *args, **kwargs):
        reviewer = request.user
        listing_id = request.data.get('listing')
        reviewee_id = request.data.get('reviewee')

        try:
            listing = Listing.objects.get(id=listing_id)
            if listing.seller == reviewer:
               return Response({"error": "You can only review users for listings you purchased."}, status=status.HTTP_403_FORBIDDEN)
            if listing.seller.id != int(reviewee_id):
                return Response({"error": "Reviewee must be the seller of the purchased listing."}, status=status.HTTP_400_BAD_REQUEST)
        except Listing.DoesNotExist:
            return Response({"error": "Listing does not exist."}, status=status.HTTP_404_NOT_FOUND)

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
     #   if instance.reviewer != request.user:
     #       return Response({"error": "You can only update your own reviews."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['get'], url_path='user-reviews')
    def user_reviews(self, request, pk=None):
        user = User.objects.get(pk=pk)
        reviews = Review.objects.filter(reviewee=user)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='average-rating')
    def average_rating(self, request, pk=None):
        user = User.objects.get(pk=pk)
        average_rating = Review.objects.filter(reviewee=user).aggregate(Avg('rating'))['rating__avg']
        return Response({"average_rating": average_rating})
   
   


@api_view(['GET'])
def get_listing(request, listing_id):
    try:
        listing = Listing.objects.get(id=listing_id)
        serializer = ListingSerializer(listing)
        return Response(serializer.data)
    except Listing.DoesNotExist:
        return Response({'detail': 'Listing not found'}, status=status.HTTP_404_NOT_FOUND)
    