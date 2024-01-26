from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('db/', include('DbApplication.urls')),
    # Other URL patterns for your project
]
