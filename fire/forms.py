from django import forms
from django.forms import ModelForm
from .models import Locations, Incident, FireStation, WeatherCondition, FireTruck, FireFighter


class LocationForm(ModelForm):
    class Meta:
        model = Locations
        fields = "__all__"


class Incident_Form(ModelForm):
    date_time = forms.DateTimeField(
        label="Incident Date & Time",
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'})
    )

    class Meta:
        model = Incident
        fields = "__all__"


class FireStationzForm(ModelForm):
    class Meta:
        model = FireStation
        fields = "__all__"


class WeatherConditionForm(ModelForm):
    class Meta:
        model = WeatherCondition
        fields = "__all__"


class FireTruckForm(ModelForm):
    class Meta:
        model = FireTruck
        fields = "__all__"


class FireFighterForm(forms.ModelForm):
    class Meta:
        model = FireFighter
        fields = "__all__" 