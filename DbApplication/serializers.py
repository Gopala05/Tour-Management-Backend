from rest_framework import serializers
from .models import AdventurePlaceList, Destination, Travel, User
from .models import CustomerDetail
from .models import AdventurePackage
from .models import BookingDetail


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class FeedbackSerializer(serializers.Serializer):
    feedback = serializers.CharField(max_length=255)


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = '__all__'



class TravelSerializer(serializers.ModelSerializer):
    destination_id = DestinationSerializer(read_only=True)  # Nested serializer for destination details

    class Meta:
        model = Travel
        fields = '__all__'  # Includes all fields from the Travel model




class AdventurePlaceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdventurePlaceList
        fields = '__all__'  # or list the fields explicitly

class AdventurePackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdventurePackage
        fields = ('adventure_id', 'name', 'activities', 'images')


class CustomerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDetail
        fields = ['id', 'name', 'mobile_number', 'email']


class UserSignInSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class BookingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingDetail
        fields = ['id', 'name', 'mobile_number', 'email', 'address_proof', 'dates', 'package_details', 'payment_method']