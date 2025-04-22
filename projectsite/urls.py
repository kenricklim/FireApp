from django.urls import path
from django.contrib import admin
from fire.views import (
    HomePageView,
    ChartView,
    PieCountbySeverity,
    LineCountbyMonth,
    MultilineIncidentTop3Country,
    multipleBarbySeverity,
    map_station,
    fire_incident_map,
    IncidentListView,
    IncidentCreateView,
    IncidentUpdateView,
    IncidentDeleteView,
    LocationListView,
    LocationCreateView,
    LocationUpdateView,
    LocationDeleteView,
    FireStationListView,
    FireStationCreateView,
    FireStationUpdateView,
)

urlpatterns = [
    # Main views
    path("admin/", admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('dashboard-chart', ChartView.as_view(), name='dashboard-chart'),

    # Chart data APIs
    path('chart/pie/severity/', PieCountbySeverity, name='chart-pie-severity'),
    path('chart/line/month/', LineCountbyMonth, name='chart-line-month'),
    path('chart/multiline/top3/', MultilineIncidentTop3Country, name='chart-multiline-top3'),
    path('chart/bar/severity/', multipleBarbySeverity, name='chart-bar-severity'),

    # Map views
    path('map/stations/', map_station, name='map_station'),

    # Map View: Fire Incidents
    path('map/fire_incident/', fire_incident_map, name='fire_incidents_map'),
    
     # Fire Station URLs
    path('stations/', FireStationListView.as_view(), name='station_list'),
    path('station/create/', FireStationCreateView.as_view(), name='station_create'),
    path('station/<int:pk>/update/', FireStationUpdateView.as_view(), name='station_update'),

    # Incident URLs
    path('incidents/', IncidentListView.as_view(), name='incident-list'),
    path('incident/create/', IncidentCreateView.as_view(), name='incident-add'),
    path('incident/<int:pk>/update/', IncidentUpdateView.as_view(), name='incident-update'),
    path('incident/<int:pk>/delete/', IncidentDeleteView.as_view(), name='incident-delete'),
    
    #location   
    path('locations/', LocationListView.as_view(), name='location-list'),
    path('location/create/', LocationCreateView.as_view(), name='location-add'),
    path('location/<int:pk>/update/', LocationUpdateView.as_view(), name='location-update'),
    path('location_list/<pk>/delete/', LocationDeleteView.as_view(), name='location-delete'),
]
