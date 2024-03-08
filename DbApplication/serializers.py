from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        
class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = '__all__'

class UserSignInSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

class AdventurePackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdventurePackage
        fields = '__all__'

class BookingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingDetail
        fields = '__all__'
        
class TravelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Travels
        fields = '__all__'

class UserFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFeedback
        fields = "__all__"

class TopDestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopDestination
        fields = '__all__'