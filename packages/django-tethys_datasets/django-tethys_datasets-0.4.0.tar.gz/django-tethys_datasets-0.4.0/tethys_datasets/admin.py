from django.contrib import admin
from .models import DatasetService


class DatasetServiceAdmin(admin.ModelAdmin):
    """
    Admin model for Web Processing Service Model
    """
    fields = ('name', 'engine', 'apikey', 'endpoint', 'username', 'password')


admin.site.register(DatasetService, DatasetServiceAdmin)
