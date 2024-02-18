from rest_framework import serializers
from .models import *

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
    destination_id = DestinationSerializer(read_only=True)

    class Meta:
        model = Travel
        fields = '__all__'

class AdventurePlaceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdventurePlaceList
        fields = '__all__' 

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
        fields = '__all__'

class UserFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFeedback
        fields = ['id', 'user', 'feedback_text', 'rating', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

class TopDestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopDestination
        fields = '__all__'