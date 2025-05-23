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
    FireStationDeleteView,
    maps,
    fighter_list,
    fighter_create,
    fighter_edit,
    fighter_delete,
    truck_list,
    truck_create,
    truck_edit,
    truck_delete,
    weather_list,
    weather_create,
    weather_edit,
    weather_delete,
    dashboard_chart,
)

urlpatterns = [
    # Main views
    path("admin/", admin.site.urls),
    path('', HomePageView.as_view(), name='home'),
    path('dashboard-chart', ChartView.as_view(), name='dashboard-chart'),
    path('maps/', maps, name='maps'),
    path('charts/', dashboard_chart, name='charts'),

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
    path('stations/create/', FireStationCreateView.as_view(), name='station_create'),
    path('stations/<int:pk>/edit/', FireStationUpdateView.as_view(), name='station_edit'),
    path('stations/<int:pk>/delete/', FireStationDeleteView.as_view(), name='station_delete'),

    # Fire Fighter URLs
    path('fighters/', fighter_list, name='fighter_list'),
    path('fighters/create/', fighter_create, name='fighter_create'),
    path('fighters/<int:pk>/edit/', fighter_edit, name='fighter_edit'),
    path('fighters/<int:pk>/delete/', fighter_delete, name='fighter_delete'),

    # Fire Truck URLs
    path('trucks/', truck_list, name='truck_list'),
    path('trucks/create/', truck_create, name='truck_create'),
    path('trucks/<int:pk>/edit/', truck_edit, name='truck_edit'),
    path('trucks/<int:pk>/delete/', truck_delete, name='truck_delete'),

    # Weather Condition URLs
    path('weather/', weather_list, name='weather_list'),
    path('weather/create/', weather_create, name='weather_create'),
    path('weather/<int:pk>/edit/', weather_edit, name='weather_edit'),
    path('weather/<int:pk>/delete/', weather_delete, name='weather_delete'),

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
