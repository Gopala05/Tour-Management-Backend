from django.db import models
from django.conf import settings

RATING_CHOICES = [
    (1, '1 - Poor'),
    (2, '2 - Below Average'),
    (3, '3 - Average'),
    (4, '4 - Good'),
    (5, '5 - Excellent'),
]

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
    first_name = models.CharField(max_length=30, blank=False, null=False)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    mobile_number = models.CharField(max_length=10, blank=False, null=False)
    email = models.EmailField(unique=True)
    aadhar_number = models.CharField(max_length=12, blank=False, null=False)
    gender = models.CharField(max_length=10, blank=False, null=False)
    address = models.TextField(null=True,blank=True)
    date_of_birth = models.DateField(blank=False, null=False)
    
    class Meta:
        db_table = 'Users'
        
class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    admin_name = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)
    mobile_number = models.CharField(max_length=10, blank=False, null=False)
    email = models.EmailField(unique=True)
    
    class Meta:
        db_table = 'Admin'

class AdventurePackage(models.Model):
    adventure_id = models.AutoField(primary_key=True)
    locations = models.CharField(max_length=255)
    no_of_activities = models.IntegerField(default= 1)
    no_of_places = models.IntegerField(default= 1)
    cost = models.CharField(max_length=100, blank=False, null=False)
    start_date = models.DateField(blank=False, null=False)
    duration = models.CharField(max_length=100, blank=False, null=False)
    created_by = models.ForeignKey(Admin, on_delete=models.CASCADE)

    class Meta:
        db_table = 'AdventurePackage'

class BookingDetail(models.Model):
    booking_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=10, blank=False, null=False)
    email = models.EmailField(blank=False, null=False)
    package_name = models.CharField(max_length=255)
    booking_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    package_id = models.ForeignKey(AdventurePackage, on_delete=models.CASCADE)
    no_of_passengers = models.IntegerField(default=1)
    total_cost = models.CharField(max_length=100, blank=False, null=False)
    cost_per_person = models.CharField(max_length=100, blank=False, null=False)
    class Meta:
        db_table = 'BookingDetail'

class Travels(models.Model):
    travel_id = models.AutoField(primary_key=True)
    locations = models.CharField(max_length=255)
    user_id = models.ForeignKey('User', on_delete=models.CASCADE)
    booking_id = models.ForeignKey('BookingDetail', on_delete=models.CASCADE)
    no_of_passengers = models.IntegerField(default=1)
    total_cost = models.CharField(max_length=100,default= 0, blank=False, null=False)
    cost_per_person = models.CharField(max_length=100,default= 0, blank=False, null=False)
    start_date = models.DateField(blank=False, null=False)
    booked_on = models.DateField(blank=False, null=False)

    class Meta:
        db_table = 'Travels'

class UserFeedback(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=100, default="Anonymous")
    feedback_text = models.TextField(blank=False, null=False)
    rating = models.IntegerField(choices=RATING_CHOICES, blank=False, null=False)
    created_on = models.DateTimeField(auto_now_add=True, blank=False, null=False)

    class Meta:
        ordering = ['-created_on']
        db_table = 'User Feedback'
    
class TopDestinations(models.Model):
    destination_id = models.AutoField(primary_key=True)
    place_names = models.CharField(max_length=255)
    no_of_places = models.IntegerField(default=1)
    no_of_activities = models.IntegerField(default=1)
    price = models.CharField(max_length=100, blank=False, null=False)
    created_by = models.ForeignKey(Admin, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'Top_Destinations'