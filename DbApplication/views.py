from django.db import transaction
from django.shortcuts import get_object_or_404
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
import json

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
        
        if User.objects.filter(aadhar_number=data['aadhar_number']).exists():
            return Response({'message': 'Aadhar already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(mobile_number=data['mobile_number']).exists():
            return Response({'message': 'Mobile Number already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = UserSerializer(data=data)
        
        if serializer.is_valid():
            user = serializer.save()

            try:
                keycloak_admin = getKeycloakAdmin()
                new_user = keycloak_admin.create_user({
                        "username": user.username,
                        "enabled": True,
                        "firstName": user.first_name,
                        "lastName": user.last_name,
                        "credentials": [{"value": user.first_name,"type": "password"}]
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
        
class UserSignIn(APIView):
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
                return Response({'message': 'Sign In successful','user':user_data,'token':resp}, status=status.HTTP_202_ACCEPTED)
            except Exception as e:
                logger.error(e)
                return JsonResponse({"message": "Error Validating user credentials."},status=status.HTTP_503_SERVICE_UNAVAILABLE)
        else:
            return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
        
class AdminSignup(APIView):
    """
    API endpoint for admin signup.
    """
    def post(self, request):
        data = request.data

        if Admin.objects.filter(admin_name=data['admin_name']).exists():
            return Response({'message': 'Admin name already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        if Admin.objects.filter(email=data['email']).exists():
            return Response({'message': 'Email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if Admin.objects.filter(mobile_number=data['mobile_number']).exists():
            return Response({'message': 'Mobile Number already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = AdminSerializer(data=data)
        
        if serializer.is_valid():
            admin = serializer.save()

            try:
                keycloak_admin = getKeycloakAdmin()
                new_user = keycloak_admin.create_user({
                        "username": admin.admin_name,
                        "enabled": True,
                        "credentials": [{"value": admin.password,"type": "password"}]
                    }
                )  
                                        
            except Exception as e:
                admin.delete()
                print(e)
                logger.error(e)
                return JsonResponse({"message": "Error occurred when creating user."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            response = {
                'message': 'User registered successfully',
                'user': serializer.data,
            }
            return Response(response, status=status.HTTP_201_CREATED)
        
class AdminSignIn(APIView):
    def post(self, request):
        admin_name = request.data.get('admin_name', '')
        password = request.data.get('password', '')
        try:
            admin = Admin.objects.get(admin_name=admin_name)
        except Admin.DoesNotExist:
            return Response({'error': 'Admin Doesnt exist'}, status=status.HTTP_404_NOT_FOUND)

        if (password == admin.password):
            admin_data = {
                'admin_id': admin.admin_id,
                'admin_name': admin.admin_name,
                'mobile_number': admin.mobile_number,
                'email': admin.email,
            }
            try:
                keycloak_openid = getKeycloak()
                try:
                    username = admin.admin_name
                    password = admin.password
                    
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
                return Response({'message': 'Sign In successful','admin':admin_data,'token':resp}, status=status.HTTP_202_ACCEPTED)
            except Exception as e:
                logger.error(e)
                return JsonResponse({"message": "Error Validating user credentials."},status=status.HTTP_503_SERVICE_UNAVAILABLE)
        else:
            return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
        
class GetUser(APIView):
    def post(self, request):
        id = self.request.query_params.get('user_id')

        try:
            user = User.objects.get(user_id=id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user).data  
        return Response({'user': serializer}, status=status.HTTP_200_OK)
    
class AdventurePackages(APIView):
    def get(self, request):
        try:
            data = AdventurePackage.objects.all()
            serializer = AdventurePackageSerializer(data, many=True)
            return Response({"places": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Unable to retrieve adventure place details.'}, status=500)
        
class CreateAdventurePackagres(APIView):
    def post(self, request):
        payload = request.data
        if AdventurePackage.objects.filter(locations=payload['locations']).exists():
            return Response({'message': 'Adventure Package already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = AdventurePackageSerializer(data=payload)
        if serializer.is_valid():
            serializer.save()
            return Response({"details": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class BookingDetails(APIView):

    def get(self, request):
        booking_id = self.request.query_params.get('booking_id')

        if booking_id:
            instance = BookingDetail.objects.filter(booking_id=booking_id).first()
            if instance:
                serializer = BookingDetailSerializer(instance)
                return Response({"details": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            data = BookingDetail.objects.all()
            serializer = BookingDetailSerializer(data, many=True)
            return Response({"details": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request ):
        try:
            user_id = request.data.get('user_id')
            adventure_id = request.data.get('adventure_id')
            total_cost = request.data.get('total_cost')
            passengers = request.data.get('no_of_passengers')

            # Fetch user details
            user = get_object_or_404(User, user_id=user_id)

            # Fetch adventure place details
            adventure_place = get_object_or_404(AdventurePackage, adventure_id=adventure_id)
            
            if BookingDetail.objects.filter(package_id=adventure_id, user_id=user_id).exists():
                return Response({'message': 'Booking for this Package already exists. Try Booking from another Account'}, status=status.HTTP_400_BAD_REQUEST)

            # Create booking detail
            booking_detail = BookingDetail.objects.create(
                name=user.username,
                mobile_number=user.mobile_number,
                email=user.email,
                package_name=adventure_place.locations,
                activities=adventure_place.activities,
                total_cost=total_cost,
                user_id = user,
                package_id = adventure_place,
                no_of_passengers = passengers,
                cost_per_person = adventure_place.cost
            )
            
            Travels.objects.create(
                locations = adventure_place.locations,
                price = adventure_place.cost,
                user_id = user,
                booking_id = booking_detail,
                start_date = adventure_place.start_date,
                booked_on = booking_detail.booking_date
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
                'address': user.address,
                'date_of_birth': user.date_of_birth,
                'start_date': adventure_place.start_date,
                'package_name': booking_detail.package_name,
                'activities': booking_detail.activities
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TravelDetails(APIView):
    def get(self, request):
        data = Travels.objects.all()
        serializer = TravelSerializer(data, many=True)
        return Response({"details": serializer.data}, status=status.HTTP_200_OK)

class UserFeedbackCreate(generics.CreateAPIView):
    queryset = UserFeedback.objects.all()
    serializer_class = UserFeedbackSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserFeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class UserFeedBackDetails(APIView):
    def get(self, request):
        data = UserFeedback.objects.all()
        serializer = UserFeedbackSerializer(data, many=True)
        return Response({"details": serializer.data}, status=status.HTTP_200_OK)
    
# class Logout(APIView):
#     permission_classes = []

#     def post(self, request):
#         if request.auth:
#             request.auth.delete()

#         return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)

class TopDestinations(generics.ListAPIView):
    def get(self, request):
        destination_id = self.request.query_params.get('destination_id')

        if destination_id:
            instance = TopDestination.objects.filter(destination_id=destination_id).first()
            if instance:
                serializer = TopDestinationSerializer(instance)
                return Response({"details": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Top-Destinations not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            data = TopDestination.objects.all()
            serializer = TopDestinationSerializer(data, many=True)
            return Response({"details": serializer.data}, status=status.HTTP_200_OK)
    
    def post(self, request):
        payload = request.data
        serializer = TopDestinationSerializer(data= payload)
        
        if serializer.is_valid():
            details = serializer.save()
            
            return Response({"details": serializer.data}, status=status.HTTP_201_CREATED)
        return Response("Unable to create", status=status.HTTP_400_BAD_REQUEST)
    
class TokenRefresh(APIView):
     def post(self,request):
        try:
            try:
                body = json.loads(request.body.decode("utf-8"))
                
                refresh_token = body['refresh_token']
            except Exception as e:
                logger.error(e)
                return JsonResponse({"message": "Pass Refresh token provided during login."},status=status.HTTP_400_BAD_REQUEST)

            keycloak_openid = getKeycloak()
            token = keycloak_openid.refresh_token(refresh_token)

            resp = {
                "token" : token['access_token'], 
                "expires_in" : token['expires_in'],
                "refresh_token" : token['refresh_token'],
                "refresh_expires_in" : token['refresh_expires_in']
                }

        except Exception as e:
            logger.error(e)
            return JsonResponse({"message": "Error Refreshing the token. Session might have expired, login again."},status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        return JsonResponse(resp,status=status.HTTP_200_OK)