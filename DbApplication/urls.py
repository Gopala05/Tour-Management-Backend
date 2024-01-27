from django.contrib import admin
from django.urls import path, re_path
from DbApplication import views
from .views import (
    UserSignInAPIView, AdventurePlaceListAPIView,
    AdventurePlaceDetailAPIView, CustomerDetailCreateAPIView,
    AdventurePackageDetailAPIView, BookingDetailCreateAPIView,
    FeedbackCreateAPIView, LogoutAPIView,UserSignup,GetUserAPIView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/create_user', UserSignup.as_view(), name='create_user'),
    path('api/sign_in', UserSignInAPIView.as_view(), name='sign_in'),
    path('api/get_user', GetUserAPIView.as_view(), name='get_user'),
    path('api/places', AdventurePlaceListAPIView.as_view(), name='adventure_place_list'),
    path('api/place', AdventurePlaceDetailAPIView.as_view(), name='adventure_place_detail'),
    path('api/customer-details', CustomerDetailCreateAPIView.as_view(), name='customer_detail_create'),
    path('api/place/<int:id>/packages', AdventurePackageDetailAPIView.as_view(), name='adventure_package_detail'),
    path('api/booking-details', BookingDetailCreateAPIView.as_view(), name='booking_detail_create'),
    path('api/feedback', FeedbackCreateAPIView.as_view(), name='feedback_create'),
    path('api/logout', LogoutAPIView.as_view(), name='logout'),
    re_path("user", views.UserSignup.as_view())
]
