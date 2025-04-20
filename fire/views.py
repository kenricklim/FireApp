from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.db import connection
from django.db.models import Q

from fire.models import Locations, Incident, FireStation
from fire.forms import Incident_Form ,LocationForm, FireStationzForm
from datetime import datetime


# Home Page View
class HomePageView(ListView):
    model = Locations
    context_object_name = 'home'
    template_name = "home.html"


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
        print(cursor.fetchall())

    months = set(str(i).zfill(2) for i in range(1, 13))
    result = {}

    for country, month, count in rows:
        if country not in result:
            result[country] = {m: 0 for m in months}
        result[country][month] = count

    while len(result) < 3:
        result[f"Country {len(result) + 1}"] = {m: 0 for m in months}

    return JsonResponse({k: dict(sorted(v.items())) for k, v in result.items()})


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
    model = FireStationzForm
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

class FireStationCreateView(CreateView):
    model = FireStationzForm
    form_class = FireStationzForm
    template_name = 'station_add.html'
    success_url = reverse_lazy('station-list')

    def form_valid(self, form):
        station_name = form.instance.name
        messages.success(self.request, f'Fire Station "{station_name}" created successfully!')
        return super().form_valid(form)

class FireStationUpdateView(UpdateView):
    model = FireStationzForm
    form_class = FireStationzForm
    template_name = 'station_edit.html'
    success_url = reverse_lazy('station-list')

    def form_valid(self, form):
        station_name = form.instance.name
        messages.success(self.request, f'Fire Station "{station_name}" updated successfully!')
        return super().form_valid(form)
    
class FireStationDeleteView(DeleteView):
    model = FireStationzForm
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