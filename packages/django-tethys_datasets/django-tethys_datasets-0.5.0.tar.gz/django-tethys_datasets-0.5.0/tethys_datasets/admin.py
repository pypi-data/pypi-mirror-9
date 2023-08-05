from django.contrib import admin
from .models import DatasetService, SpatialDatasetService
from django.forms import ModelForm, PasswordInput


class DatasetServiceForm(ModelForm):
    class Meta:
        model = DatasetService
        widgets = {
            'password': PasswordInput(),
        }


class SpatialDatasetServiceForm(ModelForm):
    class Meta:
        model = SpatialDatasetService
        widgets = {
            'password': PasswordInput(),
        }


class DatasetServiceAdmin(admin.ModelAdmin):
    """
    Admin model for Web Processing Service Model
    """
    form = DatasetServiceForm
    fields = ('name', 'engine', 'endpoint', 'apikey', 'username', 'password')


class SpatialDatasetServiceAdmin(admin.ModelAdmin):
    """
    Admin model for Spatial Dataset Service Model
    """
    form = SpatialDatasetServiceForm
    fields = ('name', 'engine', 'endpoint', 'apikey', 'username', 'password')


admin.site.register(DatasetService, DatasetServiceAdmin)
admin.site.register(SpatialDatasetService, SpatialDatasetServiceAdmin)
