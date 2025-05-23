from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.db import connection
from django.db.models import Q
from django.core.paginator import Paginator

from fire.models import Locations, Incident, FireStation, FireFighter, FireTruck, WeatherCondition
from fire.forms import Incident_Form, LocationForm, FireStationzForm, FireFighterForm, FireTruckForm, WeatherConditionForm
from datetime import datetime


# Home Page View
class HomePageView(ListView):
    model = Locations
    context_object_name = 'home'
    template_name = "home.html"


# Maps View
def maps(request):
    return render(request, 'maps.html')


# Widgets View
def widgets(request):
    context = {
        'stations_count': FireStation.objects.count(),
        'fighters_count': FireFighter.objects.count(),
    }
    return render(request, 'widgets.html', context)


# Chart Page View
class ChartView(ListView):
    template_name = 'chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self, *args, **kwargs):
        pass


# Chart Data: Pie by Severity Level
def PieCountbySeverity(request):
    try:
        query = '''
        SELECT severity_level, COUNT(*) as count
        FROM fire_incident
        GROUP BY severity_level
        '''
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
        data = {severity: count for severity, count in rows} if rows else {}
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def LineCountbyMonth(request):
    try:
        current_year = datetime.now().year
        result = {month: 0 for month in range(1, 13)}
        
        incidents = Incident.objects.filter(
            date_time__year=current_year
        ).values_list('date_time', flat=True)
        
        for date_time in incidents:
            result[date_time.month] += 1

        month_names = {
            1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 
            5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
            9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
        }

        return JsonResponse(
            {month_names[month]: result[month] for month in range(1, 13)}
        )
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Chart Data: Multi-Line for Top 3 Countries
def MultilineIncidentTop3Country(request):
    query = '''
    SELECT 
        fl.country,
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM 
        fire_incident fi
    JOIN 
        fire_locations fl ON fi.location_id = fl.id
    WHERE 
        fl.country IN (
            SELECT 
                fl_top.country
            FROM 
                fire_incident fi_top
            JOIN 
                fire_locations fl_top ON fi_top.location_id = fl_top.id
            WHERE 
                strftime('%Y', fi_top.date_time) = strftime('%Y', 'now')
            GROUP BY 
                fl_top.country
            ORDER BY 
                COUNT(fi_top.id) DESC
            LIMIT 3
        )
        AND strftime('%Y', fi.date_time) = strftime('%Y', 'now')
    GROUP BY 
        fl.country, month
    ORDER BY 
        fl.country, month;
    '''

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()  # ACTUALLY STORE THE RESULTS

    months = [str(i) for i in range(1, 13)]  # Single-digit month keys
    result = {}

    for country, month, count in rows:
        # Convert two-digit month to single-digit
        month = str(int(month))  # '01' → '1', '12' → '12'
        country = country or f"Country {len(result) + 1}"  # Handle nulls
        
        if country not in result:
            result[country] = {m: 0 for m in months}
        
        result[country][month] = count

    # Ensure exactly 3 countries
    while len(result) < 3:
        dummy_country = f"Country {len(result) + 1}"
        result[dummy_country] = {m: 0 for m in months}

    return JsonResponse({
        country: {month: data[month] for month in months} 
        for country, data in result.items()
    })


# Chart Data: Multiple Bars by Severity per Month
def multipleBarbySeverity(request):
    query = '''
    SELECT 
        fi.severity_level,
        strftime('%m', fi.date_time) AS month,
        COUNT(fi.id) AS incident_count
    FROM 
        fire_incident fi
    GROUP BY fi.severity_level, month
    '''

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    months = set(str(i).zfill(2) for i in range(1, 13))
    result = {}

    for level, month, count in rows:
        if level not in result:
            result[str(level)] = {m: 0 for m in months}
        result[str(level)][month] = count

    return JsonResponse({k: dict(sorted(v.items())) for k, v in result.items()})


# Map View: Fire Stations
def map_station(request):
    stations = FireStation.objects.values('name', 'latitude', 'longitude')
    stations = [{
        'name': s['name'],
        'latitude': float(s['latitude']),
        'longitude': float(s['longitude'])
    } for s in stations]

    return render(request, 'map_station.html', {'fireStations': stations})


# Map View: Fire Incidents
def fire_incident_map(request):
    incidents = Locations.objects.values('name', 'latitude', 'longitude')
    incidents = [{
        'name': i['name'],
        'latitude': float(i['latitude']),
        'longitude': float(i['longitude'])
    } for i in incidents]

    return render(request, 'fire_incident_map.html', {'fireIncidents': incidents})


# Incident: Create View
class IncidentCreateView(CreateView):
    model = Incident
    form_class = Incident_Form
    template_name = 'incident_add.html'
    success_url = reverse_lazy('incident-list')

    def form_valid(self, form):
        description = form.instance.description[:50] + "..." if len(form.instance.description) > 50 else form.instance.description
        messages.success(self.request, f'Incident "{description}" created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['incident_list'] = self.success_url
        return context


# Incident: Update View
class IncidentUpdateView(UpdateView):
    model = Incident
    form_class = Incident_Form
    template_name = 'incident_edit.html'
    success_url = reverse_lazy('incident-list')

    def form_valid(self, form):
        description = form.instance.description[:50] + "..." if len(form.instance.description) > 50 else form.instance.description
        messages.success(self.request, f'Incident "{description}" updated successfully!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['incident_list'] = self.success_url
        return context


# Incident: Delete View
class IncidentDeleteView(DeleteView):
    model = Incident
    template_name = 'incident_del.html'
    success_url = reverse_lazy('incident-list')
    context_object_name = 'incident'

    def form_valid(self, form):
        response = super().form_valid(form)
        description = self.object.description[:50] + "..." if len(self.object.description) > 50 else self.object.description
        messages.success(self.request, f'Successfully deleted incident: "{description}"')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Delete Incident #{self.object.id}"
        context['incident_list'] = self.success_url
        return context


# Incident: List/Search View
class IncidentListView(ListView):
    model = Incident
    template_name = 'incident_list.html'
    context_object_name = 'object_list'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        query = self.request.GET.get("q")
        if query:
            qs = qs.filter(
                Q(description__icontains=query) |
                Q(severity_level__icontains=query) |
                Q(location__name__icontains=query) |
                Q(date_time__icontains=query)
            )
        return qs


class LocationListView(ListView):
    model = Locations
    template_name = 'location_list.html'
    context_object_name = 'object_list'
    paginate_by = 10

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        query = self.request.GET.get("q")
        if query:
            qs = qs.filter(
                Q(name__icontains=query) |
                Q(address__icontains=query) |
                Q(city__icontains=query) |
                Q(country__icontains=query)
            )
        return qs

class LocationCreateView(CreateView):
    model = Locations
    form_class = LocationForm
    template_name = 'location_add.html'
    success_url = reverse_lazy('location-list')

    def form_valid(self, form):
        name = form.instance.name
        messages.success(self.request, f'Location "{name}" created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['loc_list'] = self.success_url  # Pass the cancel URL to template
        return context

class LocationUpdateView(UpdateView):
    model = Locations
    form_class = LocationForm
    template_name = 'location_edit.html'
    success_url = reverse_lazy('location-list')

    def form_valid(self, form):
        name = form.instance.name
        messages.success(self.request, f'Location "{name}" updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['location_list'] = self.success_url  # Pass the cancel URL to template
        return context

class LocationDeleteView(DeleteView):
    model = Locations
    template_name = 'location_del.html'
    success_url = reverse_lazy('location-list')
    context_object_name = 'location'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Delete Location #{self.object.id}"
        return context

    def form_valid(self, form):
        name = self.object.name
        response = super().form_valid(form)
        messages.success(self.request, 
            f'Location "{name}" was successfully deleted.',
            extra_tags='danger'
        )
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['loc_list'] = self.success_url  # Pass the cancel URL to template
        return context
    
    
class FireStationListView(ListView):
    model = FireStation
    template_name = 'station_list.html'
    context_object_name = 'object_list'
    paginate_by = 10
    
    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        query = self.request.GET.get("q")
        if query:
            qs = qs.filter(
                Q(name__icontains=query) |
                Q(address__icontains=query) |
                Q(city__icontains=query) |
                Q(country__icontains=query)
            )
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Fire Stations'
        context['create_url'] = 'station_create'
        context['edit_url'] = 'station_edit'
        context['delete_url'] = 'station_delete'
        context['list_url'] = 'station_list'
        return context

class FireStationCreateView(CreateView):
    model = FireStation
    form_class = FireStationzForm
    template_name = 'station_add.html'
    success_url = reverse_lazy('station_list')

    def form_valid(self, form):
        station_name = form.instance.name
        messages.success(self.request, f'Fire Station "{station_name}" created successfully!')
        return super().form_valid(form)

class FireStationUpdateView(UpdateView):
    model = FireStation
    form_class = FireStationzForm
    template_name = 'station_edit.html'
    success_url = reverse_lazy('station_list')

    def form_valid(self, form):
        station_name = form.instance.name
        messages.success(self.request, f'Fire Station "{station_name}" updated successfully!')
        return super().form_valid(form)
    
class FireStationDeleteView(DeleteView):
    model = FireStation
    template_name= 'station_del.html'
    success_url = reverse_lazy('station-list')
    
    def form_valid(self, form):
        station_name = form.instance.name
        messages.success(self.request, f'Fire Station "{station_name}" deleted successfully!')
        return super().form_valid(form)

def dashboard_chart(request):
    context = {

    }
    return render(request, 'dashboard/chart.html', context)

# Fire Station Views
def station_list(request):
    search_query = request.GET.get('search', '')
    stations = FireStation.objects.all()
    
    if search_query:
        stations = stations.filter(
            Q(name__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    paginator = Paginator(stations, 10)  # Show 10 stations per page
    page = request.GET.get('page')
    stations = paginator.get_page(page)
    
    return render(request, 'fire/station_list.html', {'stations': stations})

def station_create(request):
    if request.method == 'POST':
        # Handle form submission
        name = request.POST.get('name')
        address = request.POST.get('address')
        city = request.POST.get('city')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        FireStation.objects.create(
            name=name,
            address=address,
            city=city,
            latitude=latitude,
            longitude=longitude
        )
        messages.success(request, 'Fire Station created successfully!')
        return redirect('station_list')
    
    return render(request, 'fire/station_form.html')

def station_edit(request, pk):
    station = get_object_or_404(FireStation, pk=pk)
    if request.method == 'POST':
        station.name = request.POST.get('name')
        station.address = request.POST.get('address')
        station.city = request.POST.get('city')
        station.latitude = request.POST.get('latitude')
        station.longitude = request.POST.get('longitude')
        station.save()
        messages.success(request, 'Fire Station updated successfully!')
        return redirect('station_list')
    
    return render(request, 'fire/station_form.html', {'station': station})

def station_delete(request, pk):
    station = get_object_or_404(FireStation, pk=pk)
    if request.method == 'POST':
        station.delete()
        messages.success(request, 'Fire Station deleted successfully!')
        return redirect('station_list')
    return render(request, 'fire/station_confirm_delete.html', {'station': station})

# Fire Fighter Views
def fighter_list(request):
    search_query = request.GET.get('search', '')
    fighters = FireFighter.objects.all()
    
    if search_query:
        fighters = fighters.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(rank__icontains=search_query)
        )
    
    paginator = Paginator(fighters, 10)
    page = request.GET.get('page')
    fighters = paginator.get_page(page)
    
    context = {
        'fighters': fighters,
        'title': 'Fire Fighters',
        'create_url': 'fighter_create'
    }
    return render(request, 'fire/fighter_list.html', context)

def fighter_create(request):
    if request.method == 'POST':
        FireFighter.objects.create(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            rank=request.POST.get('rank'),
            station_id=request.POST.get('station'),
            contact_number=request.POST.get('contact_number'),
            email=request.POST.get('email'),
            date_joined=request.POST.get('date_joined')
        )
        messages.success(request, 'Fire Fighter added successfully!')
        return redirect('fighter_list')
    
    stations = FireStation.objects.all()
    return render(request, 'fire/fighter_form.html', {'stations': stations})

def fighter_edit(request, pk):
    fighter = get_object_or_404(FireFighter, pk=pk)
    if request.method == 'POST':
        fighter.first_name = request.POST.get('first_name')
        fighter.last_name = request.POST.get('last_name')
        fighter.rank = request.POST.get('rank')
        fighter.station_id = request.POST.get('station')
        fighter.contact_number = request.POST.get('contact_number')
        fighter.email = request.POST.get('email')
        fighter.date_joined = request.POST.get('date_joined')
        fighter.save()
        messages.success(request, 'Fire Fighter updated successfully!')
        return redirect('fighter_list')
    
    stations = FireStation.objects.all()
    return render(request, 'fire/fighter_form.html', {'fighter': fighter, 'stations': stations})

def fighter_delete(request, pk):
    fighter = get_object_or_404(FireFighter, pk=pk)
    if request.method == 'POST':
        fighter.delete()
        messages.success(request, 'Fire Fighter deleted successfully!')
        return redirect('fighter_list')
    return render(request, 'fire/fighter_confirm_delete.html', {'fighter': fighter})

# Fire Truck Views
def truck_list(request):
    search_query = request.GET.get('search', '')
    trucks = FireTruck.objects.all()
    
    if search_query:
        trucks = trucks.filter(
            Q(truck_number__icontains=search_query) |
            Q(truck_type__icontains=search_query)
        )
    
    paginator = Paginator(trucks, 10)
    page = request.GET.get('page')
    trucks = paginator.get_page(page)
    
    context = {
        'trucks': trucks,
        'title': 'Fire Trucks',
        'create_url': 'truck_create'
    }
    return render(request, 'fire/truck_list.html', context)

def truck_create(request):
    if request.method == 'POST':
        FireTruck.objects.create(
            truck_number=request.POST.get('truck_number'),
            truck_type=request.POST.get('truck_type'),
            station_id=request.POST.get('station'),
            capacity=request.POST.get('capacity'),
            status=request.POST.get('status'),
            last_maintenance=request.POST.get('last_maintenance')
        )
        messages.success(request, 'Fire Truck added successfully!')
        return redirect('truck_list')
    
    stations = FireStation.objects.all()
    return render(request, 'fire/truck_form.html', {'stations': stations})

def truck_edit(request, pk):
    truck = get_object_or_404(FireTruck, pk=pk)
    if request.method == 'POST':
        truck.truck_number = request.POST.get('truck_number')
        truck.truck_type = request.POST.get('truck_type')
        truck.station_id = request.POST.get('station')
        truck.capacity = request.POST.get('capacity')
        truck.status = request.POST.get('status')
        truck.last_maintenance = request.POST.get('last_maintenance')
        truck.save()
        messages.success(request, 'Fire Truck updated successfully!')
        return redirect('truck_list')
    
    stations = FireStation.objects.all()
    return render(request, 'fire/truck_form.html', {'truck': truck, 'stations': stations})

def truck_delete(request, pk):
    truck = get_object_or_404(FireTruck, pk=pk)
    if request.method == 'POST':
        truck.delete()
        messages.success(request, 'Fire Truck deleted successfully!')
        return redirect('truck_list')
    return render(request, 'fire/truck_confirm_delete.html', {'truck': truck})

# Weather Condition Views
def weather_list(request):
    search_query = request.GET.get('search', '')
    weather_conditions = WeatherCondition.objects.all()
    
    if search_query:
        weather_conditions = weather_conditions.filter(
            Q(station__name__icontains=search_query) |
            Q(weather_description__icontains=search_query)
        )
    
    paginator = Paginator(weather_conditions, 10)
    page = request.GET.get('page')
    weather_conditions = paginator.get_page(page)
    
    context = {
        'weather_conditions': weather_conditions,
        'title': 'Weather Conditions',
        'create_url': 'weather_create'
    }
    return render(request, 'fire/weather_list.html', context)

def weather_create(request):
    if request.method == 'POST':
        WeatherCondition.objects.create(
            station_id=request.POST.get('station'),
            temperature=request.POST.get('temperature'),
            humidity=request.POST.get('humidity'),
            wind_speed=request.POST.get('wind_speed'),
            wind_direction=request.POST.get('wind_direction'),
            precipitation=request.POST.get('precipitation'),
            weather_description=request.POST.get('weather_description')
        )
        messages.success(request, 'Weather condition recorded successfully!')
        return redirect('weather_list')
    
    stations = FireStation.objects.all()
    return render(request, 'fire/weather_form.html', {'stations': stations})

def weather_edit(request, pk):
    weather = get_object_or_404(WeatherCondition, pk=pk)
    if request.method == 'POST':
        weather.station_id = request.POST.get('station')
        weather.temperature = request.POST.get('temperature')
        weather.humidity = request.POST.get('humidity')
        weather.wind_speed = request.POST.get('wind_speed')
        weather.wind_direction = request.POST.get('wind_direction')
        weather.precipitation = request.POST.get('precipitation')
        weather.weather_description = request.POST.get('weather_description')
        weather.save()
        messages.success(request, 'Weather condition updated successfully!')
        return redirect('weather_list')
    
    stations = FireStation.objects.all()
    return render(request, 'fire/weather_form.html', {'weather': weather, 'stations': stations})

def weather_delete(request, pk):
    weather = get_object_or_404(WeatherCondition, pk=pk)
    if request.method == 'POST':
        weather.delete()
        messages.success(request, 'Weather condition deleted successfully!')
        return redirect('weather_list')
    return render(request, 'fire/weather_confirm_delete.html', {'weather': weather})