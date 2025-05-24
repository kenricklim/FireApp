from django.urls import path
from . import views

urlpatterns = [
    # Existing URLs
    path('', views.HomePageView.as_view(), name='index'),
    path('maps/', views.maps, name='maps'),
    path('charts/', views.ChartView.as_view(), name='charts'),
    path('widgets/', views.widgets, name='widgets'),
    
    # Chart Data URLs
    path('chart/pie/severity/', views.PieCountbySeverity, name='pie_chart_data'),
    path('chart/line/month/', views.LineCountbyMonth, name='line_chart_data'),
    path('chart/multiline/top3/', views.MultilineIncidentTop3Country, name='multiline_chart_data'),
    path('chart/multibar/severity/', views.multipleBarbySeverity, name='multibar_chart_data'),
    
    # Fire Station URLs
    path('stations/', views.FireStationListView.as_view(), name='station_list'),
    path('stations/create/', views.FireStationCreateView.as_view(), name='station_create'),
    path('stations/<int:pk>/edit/', views.FireStationUpdateView.as_view(), name='station_edit'),
    path('stations/<int:pk>/delete/', views.FireStationDeleteView.as_view(), name='station_delete'),
    
    # Fire Fighter URLs
    path('fighters/', views.fighter_list, name='fighter_list'),
    path('fighters/create/', views.fighter_create, name='fighter_create'),
    path('fighters/<int:pk>/edit/', views.fighter_edit, name='fighter_edit'),
    path('fighters/<int:pk>/delete/', views.fighter_delete, name='fighter_delete'),
    
    # Fire Truck URLs
    path('trucks/', views.truck_list, name='truck_list'),
    path('trucks/create/', views.truck_create, name='truck_create'),
    path('trucks/<int:pk>/edit/', views.truck_edit, name='truck_edit'),
    path('trucks/<int:pk>/delete/', views.truck_delete, name='truck_delete'),
    
    # Weather Condition URLs
    path('weather/', views.weather_list, name='weather_list'),
    path('weather/create/', views.weather_create, name='weather_create'),
    path('weather/<int:pk>/edit/', views.weather_edit, name='weather_edit'),
    path('weather/<int:pk>/delete/', views.weather_delete, name='weather_delete'),
] 