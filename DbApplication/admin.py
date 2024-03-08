from django.contrib import admin
from .models import AdventurePlaceList

class AdventurePlaceListAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'activities']
    search_fields = ['name', 'activities']
    list_filter = ['name']


