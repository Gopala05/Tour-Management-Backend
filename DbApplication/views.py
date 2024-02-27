from django.db.models import Max
from xml.dom import ValidationErr
from django.db import transaction
from django.contrib.auth import authenticate,login
from django.shortcuts import get_object_or_404
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

            # Get the maximum user_id and increment it by 1
            max_user_id = User.objects.all().aggregate(Max('user_id'))['user_id__max']
            user_id = max_user_id + 1 if max_user_id is not None else 1

            user = serializer.save(user_id=user_id)  # Assuming user_id is a field in your serializer

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
    def get(self, request, format=None):
        try:
            adventure_id = request.query_params.get('id')

            if not adventure_id:
                return Response({'message': 'Adventure ID not provided in the query parameters'}, status=status.HTTP_400_BAD_REQUEST)

            # Adjust the lookup field to match your actual primary key field
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
    
    def get(self, request, format=None):
        customer_details = CustomerDetail.objects.all()
        serializer = CustomerDetailSerializer(customer_details, many=True)
        return Response(serializer.data)



class BookingDetailListCreateAPIView(generics.ListCreateAPIView):
    queryset = BookingDetail.objects.all()
    serializer_class = BookingDetailSerializer

    def get_queryset(self):
        queryset = BookingDetail.objects.all()
        booking_id = self.request.query_params.get('id')

        if booking_id:
            queryset = queryset.filter(booking_id=booking_id)
        return queryset

    def post(self, request, *args, **kwargs):
        try:
            user_id = request.data.get('user_id')
            adventure_id = request.data.get('adventure_id')
            dates = request.data.get('dates')

            # Fetch user details
            user = get_object_or_404(User, user_id=user_id)

            # Fetch adventure place details
            adventure_place = get_object_or_404(AdventurePlaceList, adventure_id=adventure_id)

            # Create booking detail
            booking_detail = BookingDetail.objects.create(
                name=user.username,
                mobile_number=user.mobile_number,
                email=user.email,
                dates=dates,
                package_name=adventure_place.package_name,
                activities=adventure_place.activities
            )

            # Prepare response data
            response_data = {
                'message': 'Booking created successfully. Thank you for your booking. Here are your booking details.',
                'booking_id': booking_detail.booking_id,
                'username': user.username,
                'password': user.password,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'mobile_number': user.mobile_number,
                'email': user.email,
                'aadhar_number': user.aadhar_number,
                'gender': user.gender,
                'alternate_mobile_number': user.alternate_mobile_number,
                'address': user.address,
                'date_of_birth': user.date_of_birth,
                'dates': booking_detail.dates,
                'package_name': booking_detail.package_name,
                'activities': booking_detail.activities
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except AdventurePlaceList.DoesNotExist:
            return Response({'error': 'AdventurePlace does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Check if 'id' query parameter is provided for retrieving a particular instance
        booking_id = self.request.query_params.get('id')
        if booking_id:
            try:
                instance = queryset.get(pk=booking_id)
                serializer = self.get_serializer(instance)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except BookingDetail.DoesNotExist:
                return Response({'error': 'BookingDetail not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)

        # Display a message for the GET request
        display_message = 'List of booking details retrieved successfully.'

        return Response({
            'status': 'Success',
            'message': display_message,
            'data': serializer.data
        }, status=status.HTTP_200_OK)



class UserFeedbackCreateAPIView(generics.CreateAPIView):
    queryset = UserFeedback.objects.all()
    serializer_class = UserFeedbackSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserFeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class LogoutAPIView(APIView):
    permission_classes = []

    def post(self, request):
        # Perform logout actions if needed
        # For example, invalidate the authentication token or session

        # Assuming you are using Token-based authentication
        if request.auth:
            request.auth.delete()

        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


class TopDestinationListAPIView(generics.ListAPIView):
    queryset = TopDestination.objects.all()
    serializer_class = TopDestinationSerializer

class TopDestinationDetailAPIView(generics.ListAPIView):
    serializer_class = TopDestinationSerializer

    def get_queryset(self):
        queryset = TopDestination.objects.all()
        destination_id = self.request.query_params.get('id')

        if destination_id:
            queryset = queryset.filter(id=destination_id)

        return queryset

class TopDestinationCreateAPIView(generics.CreateAPIView):
    queryset = TopDestination.objects.all()
    serializer_class = TopDestinationSerializer