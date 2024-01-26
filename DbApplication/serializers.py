from rest_framework import serializers
from .models import User
from .models import AdventurePlace
from .models import CustomerDetail
from .models import AdventurePackage
from .models import AdventurePlace
from .models import BookingDetail


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class FeedbackSerializer(serializers.Serializer):
    feedback = serializers.CharField(max_length=255)



class AdventurePlaceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdventurePlace
        fields = ['id', 'name', 'activities', 'images']

class CustomerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerDetail
        fields = ['id', 'name', 'mobile_number', 'email', 'id_proof', 'address_proof']

class AdventurePlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdventurePlace
        fields = ['id', 'name', 'activities', 'images']
        
class UserSignInSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

class AdventurePlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdventurePlace
        fields = ['id', 'name', 'activities', 'images']

class AdventurePackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdventurePackage
        fields = ['id', 'transport_package', 'adventure_package', 'gaming_package', 'rooms_services_package', 'cost', 'rules']

class AdventurePlaceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdventurePlace
        fields = ['id', 'name', 'transport_package', 'adventure_package', 'gaming_package', 'rooms_services_package', 'cost', 'rules']

class BookingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingDetail
        fields = ['id', 'name', 'mobile_number', 'email', 'address_proof', 'dates', 'package_details', 'payment_method']