from django.contrib import admin

from .models import Incident, Locations, FireFighter, FireStation, FireTruck, WeatherCondition

admin.site.register(Incident)
admin.site.register(Locations)
admin.site.register(FireFighter)
admin.site.register(FireStation)
admin.site.register(FireTruck)
admin.site.register(WeatherCondition)
