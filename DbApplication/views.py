from xml.dom import ValidationErr
from django.contrib.auth import authenticate,login
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.serializers import ValidationError
from django.contrib.auth.hashers import check_password
import random
import logging
from .models import AdventurePlaceList, CustomerDetail, AdventurePackage, BookingDetail,User
from .serializers import (
    UserSerializer,UserSignInSerializer,
    AdventurePlaceDetailSerializer, CustomerDetailSerializer,
    BookingDetailSerializer,
    FeedbackSerializer,AdventurePackageSerializer
)
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import AuthenticationFailed
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated


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
    
    
class AdventurePlaceListAPIView(generics.ListAPIView):
    queryset = AdventurePlaceList.objects.all()
    serializer_class = AdventurePlaceDetailSerializer

    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)

            return Response(serializer.data)
        except Exception as e:
            return Response({'message': 'Unable to retrieve adventure place details.', 'error': str(e)}, status=500)
    

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



class FeedbackCreateAPIView(generics.CreateAPIView):
    serializer_class = FeedbackSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        feedback = serializer.validated_data['feedback']
        # Process the feedback as needed (e.g., store in a database)

        response_data = {'message': 'Feedback received successfully', 'feedback': feedback}
        return Response(response_data)



class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Perform logout actions if needed
        # For example, invalidate the authentication token or session

        # Assuming you are using Token-based authentication
        request.auth.delete()

        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
