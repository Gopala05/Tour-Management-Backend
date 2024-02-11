from xml.dom import ValidationErr
from django.contrib.auth import authenticate,login
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
from rest_framework.permissions import AllowAny
from rest_framework.serializers import ValidationError
from django.contrib.auth.hashers import check_password
import random
import logging
from .models import AdventurePlaceList, CustomerDetail, AdventurePackage, BookingDetail,User,UserFeedback,TopDestination
from .serializers import (
    UserSerializer,UserSignInSerializer,
    AdventurePlaceListSerializer, CustomerDetailSerializer,
    BookingDetailSerializer,
    UserFeedbackSerializer,AdventurePackageSerializer,TopDestinationSerializer
)
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import AuthenticationFailed
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny


logger = logging.getLogger(__name__)


class UserSignup(APIView):
    """
    API endpoint for user signup.
    """
    def post(self, request):
        try:
            data = request.data
            serializer = UserSerializer(data=data)
            serializer.is_valid(raise_exception=True)

            if User.objects.filter(username=data['username']).exists():
                return Response({'message': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(email=data['email']).exists():
                return Response({'message': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()

            response_data = {
                'message': 'User registered successfully',
                'user': serializer.data
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'message': 'Unable to register user.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class GetUserAPIView(APIView):
    authentication_classes = []  # Allow unauthenticated access
    permission_classes = [IsAuthenticated]
    def post(self, request):
        username = request.data.get('username', '')
        password = request.data.get('password', '')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if check_password(password, user.password):
            serializer = UserSerializer(user)  
            return Response({'user': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
        
class UserSignInAPIView(APIView):
    def post(self, request):
        username = request.data.get('username', '')
        password = request.data.get('password', '')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if (password == user.password):
            user_data = {
                'user_id': user.user_id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'mobile_number': user.mobile_number,
                'email': user.email,
                'aadhar_number': user.aadhar_number,
                'gender': user.gender,
                'alternate_mobile_number': user.alternate_mobile_number,
            }
            return Response({'user': user_data}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
    
    

        
class AdventurePlaceListAPIView(generics.ListCreateAPIView):
    queryset = AdventurePlaceList.objects.all()
    serializer_class = AdventurePlaceListSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'message': 'Unable to retrieve adventure place details.', 'error': str(e)}, status=500)
        
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    


class AdventurePackageDetailView(APIView):
    def get(self, request, adventure_id, format=None):
        try:
            adventure_package = AdventurePackage.objects.get(adventure_id=adventure_id)
            serializer = AdventurePackageSerializer(adventure_package)
            return Response(serializer.data)
        except AdventurePackage.DoesNotExist:
            return Response({'message': 'Adventure Package not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': 'Unable to retrieve adventure package details.', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CustomerDetailAPIView(APIView):
    def post(self, request, format=None):
        serializer = CustomerDetailSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class BookingDetailCreateAPIView(generics.CreateAPIView):
    queryset = BookingDetail.objects.all()
    serializer_class = BookingDetailSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        self.send_confirmation_email(instance)

    def send_confirmation_email(self, booking_detail):
        subject = 'Booking Confirmation'
        message = f'Thank you for your booking! Here are your booking details:\n\n{booking_detail}\n\nWe look forward to serving you.'
        from_email = 'your_email@example.com'  # Update with your email
        to_email = [booking_detail.email]

        email = EmailMessage(subject, message, from_email, to_email)
        email.send()

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return response



class UserFeedbackCreateAPIView(generics.CreateAPIView):
    queryset = UserFeedback.objects.all()
    serializer_class = UserFeedbackSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None

        # Exclude 'user' from the serializer's context if it's None
        serializer_context = {'request': request}
        if user is not None:
            serializer_context['user'] = user

        serializer = self.get_serializer(data=request.data, context=serializer_context)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        return Response(serializer.data)
    

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Perform logout actions if needed
        # For example, invalidate the authentication token or session

        # Assuming you are using Token-based authentication
        request.auth.delete()

        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


class TopDestinationListAPIView(generics.ListAPIView):
    queryset = TopDestination.objects.all()
    serializer_class = TopDestinationSerializer

class TopDestinationDetailAPIView(generics.RetrieveAPIView):
    queryset = TopDestination.objects.all()
    serializer_class = TopDestinationSerializer

class TopDestinationCreateAPIView(generics.CreateAPIView):
    queryset = TopDestination.objects.all()
    serializer_class = TopDestinationSerializer