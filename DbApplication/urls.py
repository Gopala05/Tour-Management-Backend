from django.contrib import admin
from django.urls import path, re_path
from DbApplication import views
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('admin', admin.site.urls),
    path('api/create_user', UserSignup.as_view(), name='create_user'),
    path('api/sign_in', UserSignIn.as_view(), name='sign_in'),
    path('api/get_user', GetUser.as_view(), name='get_user'),
    path('api/create_admin', AdminSignup.as_view(), name='create_admin'),
    path('api/admin_sign_in', AdminSignIn.as_view(), name='admin_sign_in'),
    path('api/adventure-package', AdventurePackages.as_view(), name='adventure_package'),
    path('api/create-adventure-package', CreateAdventurePackagres.as_view(), name='create_adventure_package'),
    path('api/booking-details', BookingDetails.as_view(), name='booking_detail'),
    path('api/user-feedback', UserFeedbackCreate.as_view(), name='user_feedback_create'),
    path('api/feedbacks', UserFeedBackDetails.as_view(), name='user_feedbacks'),
    path('api/travels', TravelDetails.as_view(), name='user_travels'),
    # path('api/adventure-places', AdventurePackages.as_view(), name='adventure-place-list'),
    # path('api/customer-details', CustomerDetail.as_view(), name='customer-details-api'),
    # path('api/logout', Logout.as_view(), name='logout'),
    path('api/token-refresh', TokenRefresh.as_view(), name='token_refresh'),
    path('api/top-destination', TopDestination.as_view(), name='topdestination_detail'),
    path('api/create-top-destination', CreateTopDestinations.as_view(), name='create_top_destination'),
    path('api/update-top-destination', UpdateTopDestinations.as_view(), name='update_top_destination'),
    path('api/delete-top-destination', DeleteTopDestinations.as_view(), name='delete_top_destination'),
    re_path("user", views.UserSignup.as_view())
]
