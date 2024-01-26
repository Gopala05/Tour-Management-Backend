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
from .models import AdventurePlace, CustomerDetail, AdventurePackage, BookingDetail,User
from .serializers import (
    UserSerializer,UserSignInSerializer, AdventurePlaceSerializer,
    AdventurePlaceDetailSerializer, CustomerDetailSerializer,
    AdventurePackageSerializer, BookingDetailSerializer,
    FeedbackSerializer
)
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import AuthenticationFailed
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



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
        
class UserSignInAPIView(APIView):
    def get(self, request):
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
    queryset = AdventurePlace.objects.all()
    serializer_class = AdventurePlaceSerializer
    def get(self, request, *args, **kwargs):
        # Customize the list of adventure places with details of activities
        adventure_places = [
            {"name": "Ladakh", "activities": "Trekking, Biking, River Rafting", "images": "ladakh_image.jpg"},
            {"name": "Rishikesh", "activities": "Rafting, Yoga, Camping", "images": "rishikesh_image.jpg"},
            {"name": "Manali", "activities": "Skiing, Paragliding, Hiking", "images": "manali_image.jpg"},
            {"name": "Auli", "activities": "Skiing, Cable Car Ride, Trekking", "images": "auli_image.jpg"},
            {"name": "Gulmarg", "activities": "Skiing, Gondola Ride, Golf", "images": "gulmarg_image.jpg"},
            {"name": "Goa", "activities": "Beach Activities, Water Sports, Nightlife", "images": "goa_image.jpg"},
            {"name": "Andaman", "activities": "Scuba Diving, Snorkeling, Island Hopping", "images": "andaman_image.jpg"},
            {"name": "Caving in Meghalaya", "activities": "Caving, Adventure Exploration", "images": "meghalaya_image.jpg"},
            {"name": "Spiti", "activities": "Trekking, Monastery Visits, Camping", "images": "spiti_image.jpg"},
            {"name": "Dandeli", "activities": "River Rafting, Jungle Safari, Bird Watching", "images": "dandeli_image.jpg"},
            {"name": "Hot Air Ballooning in Jaipur", "activities": "Hot Air Ballooning, City Tour", "images": "jaipur_image.jpg"},
            {"name": "Paragliding in Bir", "activities": "Paragliding, Camping, Tibetan Colony Visit", "images": "bir_image.jpg"},
            {"name": "Shimla", "activities": "Sightseeing, Shopping, Ice Skating", "images": "shimla_image.jpg"},
            {"name": "Bike Trip to Leh", "activities": "Biking, Pangong Lake Visit, Nubra Valley", "images": "leh_image.jpg"},
        ]

        serializer = self.get_serializer(adventure_places, many=True)
        return self.get_paginated_response(serializer.data)
    
class AdventurePlaceDetailAPIView(generics.RetrieveAPIView):
    queryset = AdventurePlace.objects.all()
    serializer_class = AdventurePlaceDetailSerializer
    lookup_field = 'id'  # Assuming 'id' is the parameter to identify the adventure place

    def get(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)

            # Customize the response with additional details
            response_data = serializer.data
            response_data['description'] = self.get_activity_description(instance.name)
            
            return Response(response_data)
        except Exception as e:
            return Response({'message': 'Unable to retrieve adventure place details.'}, status=500)

    def get_activity_description(self, place_name):
        # You can customize the activity descriptions based on the adventure place
        descriptions = {
            "Ladakh": "Embark on a thrilling adventure in the majestic landscapes of Ladakh. Explore high mountain passes, "
                      "experience the culture of local monasteries, and indulge in heart-pounding biking and river rafting.",

            "Rishikesh": "Discover the spiritual charm of Rishikesh while enjoying exciting activities. Raft down the Ganges, "
                         "practice yoga by the riverside, and experience the serene beauty of this holy city.",

            "Manali": "Manali offers a perfect blend of adventure and tranquility. Enjoy skiing on the snowy slopes, "
                      "experience the thrill of paragliding, and hike in the picturesque landscapes.",

            "Auli": "Auli, known for its pristine beauty, is a paradise for ski enthusiasts. Glide through snow-covered slopes, "
                    "take a cable car ride for breathtaking views, and trek amidst the Garhwal Himalayas.",

            "Gulmarg":"Gulmarg's snow-covered slopes provide an ideal playground for snowboarding enthusiasts."
                      "Experience the thrill of carving through powdery snow against the stunning backdrop of the Pir Panjal range.",

            "Goa": "Dive into the vibrant underwater world of Goa with a scuba diving exploration."
                   "Discover coral reefs, colorful marine life, and ancient shipwrecks."
                   " Goa offers an unforgettable experience for diving enthusiasts.",

            "Andaman":"Explore the crystal-clear waters of the Andaman Islands through a captivating snorkeling adventure."
                      " Witness the diverse marine life, vibrant coral gardens, and pristine beaches",

            "Caving in Meghalaya":"Embark on an underground expedition through the caves of Meghalaya."
                                  " Discover hidden chambers, unique rock formations, and the fascinating subterranean world beneath the lush landscapes.",

            "Spiti":"Challenge yourself with a high-altitude trek in the captivating landscapes of Spiti."
                    "Trek through barren terrains, ancient monasteries, and lofty mountain passes.",

            "Dandeli ":"Experience the thrill of river rafting combined with a wildlife safari in Dandeli."
                        "Navigate through river rapids and explore the rich biodiversity of the Western Ghats.",

            "Hot Air Ballooning in Jaipur":"Soar high above the Pink City with a hot air ballooning adventure in Jaipur."
                                           "Marvel at the architectural wonders below and enjoy a bird's-eye view of the vibrant city.",

            "Paragliding in Bir":"Take to the skies with a paragliding adventure in Bir Billing, often referred to as the 'Paragliding Capital of India.' "
                                 "Soar over lush landscapes and experience the thrill of free-flying.",

            "Shimla":"Explore the picturesque surroundings of Shimla with a nature biking expedition."
                     "Ride through forested trails, apple orchards, and charming villages.",

            "Bike Trip to Leh":"Embark on a legendary bike trip to Leh, traversing high mountain passes and winding roads."
                               " Witness the stark beauty of Ladakh and the cultural richness of the region." 
            # Add descriptions for other places
        }

        return descriptions.get(place_name, "Detailed description not available.")
    


class CustomerDetailCreateAPIView(generics.CreateAPIView):
    queryset = CustomerDetail.objects.all()
    serializer_class = CustomerDetailSerializer



class AdventurePackageDetailAPIView(generics.RetrieveAPIView):
    queryset = AdventurePackage.objects.all()
    serializer_class = AdventurePackageSerializer
    lookup_field = 'id'  # Assuming 'id' is the parameter to identify the adventure package

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    


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
