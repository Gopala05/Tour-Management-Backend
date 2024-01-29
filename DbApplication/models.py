from django.db import models
from django.conf import settings



class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=60)
    password = models.CharField(max_length=45)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(default='default_email')  # Change 'email_id' to 'email'
    aadhar_number = models.CharField(max_length=20, default='default_aadhar_value')
    gender = models.CharField(max_length=10, null=True)
    alternate_mobile_number = models.CharField(max_length=15, null=True, blank=True)

    class Meta:
        db_table = 'Users'



class Travel(models.Model):
    travel_id = models.AutoField(primary_key=True)
    destination_id = models.ForeignKey('Destination', on_delete=models.CASCADE)
    amenities = models.CharField(max_length=45, blank=True, null=True)
    location = models.CharField(max_length=45)
    name = models.CharField(max_length=45)
    price_per_night = models.IntegerField()

    class Meta:
        db_table = 'Travel'

class Destination(models.Model):
    destination_id = models.AutoField(primary_key=True)
    attractions = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    name = models.CharField(max_length=45)
    travel_advisory = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'Destination'

class Itinerary(models.Model):
    itinerary_id = models.AutoField(primary_key=True)
    destination_id = models.ForeignKey(Destination, on_delete=models.CASCADE)
    travel_id = models.ForeignKey(Travel, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    end_date = models.DateField()
    start_date = models.DateField()
    title = models.CharField(max_length=255)

    class Meta:
        db_table = 'Itineraries'

class Activity(models.Model):
    activity_id = models.AutoField(primary_key=True)
    destination_id = models.ForeignKey(Destination, on_delete=models.CASCADE)
    itinerary_id = models.ForeignKey(Itinerary, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()

    class Meta:
        db_table = 'Activities'

class AdventurePlace(models.Model):
    name = models.CharField(max_length=255)
    activities = models.TextField()
    images = models.ImageField(upload_to='adventure_places/', null=True, blank=True)

    def __str__(self):
        return self.name

class CustomerDetail(models.Model):
    name = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return self.name

class AdventurePackage(models.Model):
    adventure_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    activities = models.TextField()
    images = models.ImageField(upload_to='adventure_package_images/')

    def __str__(self):
        return self.name

class BookingDetail(models.Model):
    booking_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=15)
    email = models.EmailField()
    address_proof = models.FileField(upload_to='booking_address_proofs/', null=True, blank=True)
    dates = models.DateField()
    package_details = models.TextField()
    payment_method = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name}'s Booking"
