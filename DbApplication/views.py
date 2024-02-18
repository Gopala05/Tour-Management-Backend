from django.db import transaction
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
import logging
from .models import *
from .serializers import *
from django.http import JsonResponse
from .utils import *

logger = logging.getLogger(__name__)

class UserSignup(APIView):
    """
    API endpoint for user signup.
    """
    def post(self, request):
        data = request.data

        if User.objects.filter(username=data['username']).exists():
            return Response({'message': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=data['email']).exists():
            return Response({'message': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = UserSerializer(data=data)
        
        if serializer.is_valid():
            user = serializer.save()
            try:
                username = user.username
                password = user.first_name
                firstname = user.first_name
                lastname = user.last_name
            except Exception as e:
                print(e)
                return JsonResponse({"message": "Provide required Information."},status=status.HTTP_400_BAD_REQUEST)

            try:
                keycloak_admin = getKeycloakAdmin()
                new_user = keycloak_admin.create_user({
                        "username": username,
                        "enabled": True,
                        "firstName": firstname,
                        "lastName": lastname,
                        "credentials": [{"value": password,"type": "password"}]
                    }
                )  
                                        
            except Exception as e:
                user.delete()
                print(e)
                logger.error(e)
                return JsonResponse({"message": "Error occurred when creating user."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            response = {
                'message': 'User registered successfully',
                'user': serializer.data,
            }
            return Response(response, status=status.HTTP_201_CREATED)
        
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
            try:
                keycloak_openid = getKeycloak()
                try:
                    username = user.username
                    password = user.first_name
                    
                    token = keycloak_openid.token(username,password)

                except  Exception as e:
                    logger.error(e)
                    return JsonResponse({"message": "Invalid user credentials."},status=status.HTTP_401_UNAUTHORIZED)
                
                resp = {
                    "token" : token['access_token'], 
                    "expires_in" : token['expires_in'],
                    "refresh_token" : token['refresh_token'],
                    "refresh_expires_in" : token['refresh_expires_in']
                    }
                return Response({'message': 'Sign In successful','member':user_data,'token':resp}, status=status.HTTP_202_ACCEPTED)
            except Exception as e:
                logger.error(e)
                return JsonResponse({"message": "Error Validating user credentials."},status=status.HTTP_503_SERVICE_UNAVAILABLE)
        else:
            return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
        
class GetUserAPIView(APIView):
    def post(self, request):
        username = request.data.get('username', '')
        password = request.data.get('password', '')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if (password==user.password):
            serializer = UserSerializer(user).data  
            return Response({'user': serializer}, status=status.HTTP_200_OK)

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

    def get(self):
        queryset = BookingDetail.objects.all()
        booking_id = self.request.query_params.get('id')

        if booking_id:
            queryset = queryset.filter(booking_id=booking_id)
        return queryset
    
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                response = super().create(request, *args, **kwargs)
                booking_id = response.data.get('booking_id')

                # Fetch the booking details after committing the transaction
                booking_instance = BookingDetail.objects.get(booking_id=booking_id)

                confirmation_message = f'Thank you for your booking! Here are your booking details:\n\n'
                confirmation_message += f'Booking ID: {booking_instance.booking_id}\n'
                confirmation_message += f'Name: {booking_instance.name}\n'
                confirmation_message += f'Mobile Number: {booking_instance.mobile_number}\n'
                confirmation_message += f'Email: {booking_instance.email}\n'
                confirmation_message += f'Dates: {booking_instance.dates}\n'
                confirmation_message += f'Package Details: {booking_instance.package_details}\n\n'
                confirmation_message += 'We look forward to serving you.'

                # Include booking details and confirmation message in the response
                response.data['booking_details'] = {
                    'booking_id': booking_instance.booking_id,
                    'name': booking_instance.name,
                    'mobile_number': booking_instance.mobile_number,
                    'email': booking_instance.email,
                    'dates': booking_instance.dates,
                    'package_details': booking_instance.package_details,
                }
                response.data['confirmation_message'] = confirmation_message

                return Response({
                    'status': 'Booking created successfully',
                    'subject': 'Booking Confirmation',
                    'message': confirmation_message,
                    'booking_details': response.data['booking_details']
                }, status=status.HTTP_201_CREATED)

        except BookingDetail.DoesNotExist:
            return Response({'error': 'BookingDetail not found after creation'}, status=status.HTTP_404_NOT_FOUND)
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
    permission_classes = []

    def post(self, request):
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