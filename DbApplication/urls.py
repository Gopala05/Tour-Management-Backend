from django.contrib import admin
from django.urls import path, re_path
from DbApplication import views
from .views import (
    UserSignInAPIView, AdventurePlaceListAPIView,
    CustomerDetailAPIView,
    BookingDetailCreateAPIView,
    FeedbackCreateAPIView, LogoutAPIView,UserSignup,GetUserAPIView,AdventurePackageDetailView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/create_user', UserSignup.as_view(), name='create_user'),
    path('api/sign_in', UserSignInAPIView.as_view(), name='sign_in'),
    path('api/get_user', GetUserAPIView.as_view(), name='get_user'),
    path('api/adventure-package/<int:adventure_id>/', AdventurePackageDetailView.as_view(), name='adventure-package-detail'),
    path('api/adventure-places/', AdventurePlaceListAPIView.as_view(), name='adventure-place-list'),
    path('api/customer-details/', CustomerDetailAPIView.as_view(), name='customer-details-api'),
    path('api/booking-details', BookingDetailCreateAPIView.as_view(), name='booking_detail_create'),
    path('api/feedback', FeedbackCreateAPIView.as_view(), name='feedback_create'),
    path('api/logout', LogoutAPIView.as_view(), name='logout'),
    re_path("user", views.UserSignup.as_view())
]
