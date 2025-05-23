from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Locations(BaseModel):
    name = models.CharField(max_length=150)
    latitude = models.DecimalField(
        max_digits=22, decimal_places=16, null=True, blank=True)
    longitude = models.DecimalField(
        max_digits=22, decimal_places=16, null=True, blank=True)
    address = models.CharField(max_length=150)
    city = models.CharField(max_length=150)  # can be in separate table
    country = models.CharField(max_length=150)  # can be in separate table


class Incident(BaseModel):
    SEVERITY_CHOICES = (
        ('Minor Fire', 'Minor Fire'),
        ('Moderate Fire', 'Moderate Fire'),
        ('Major Fire', 'Major Fire'),
    )
    location = models.ForeignKey(Locations, on_delete=models.CASCADE)
    date_time = models.DateTimeField(blank=True, null=True)
    severity_level = models.CharField(max_length=45, choices=SEVERITY_CHOICES)
    description = models.CharField(max_length=250)


class FireStation(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class FireFighter(models.Model):
    RANK_CHOICES = [
        ('CHIEF', 'Fire Chief'),
        ('CAPTAIN', 'Captain'),
        ('LIEUTENANT', 'Lieutenant'),
        ('SENIOR', 'Senior Firefighter'),
        ('FIREFIGHTER', 'Firefighter'),
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    rank = models.CharField(max_length=20, choices=RANK_CHOICES)
    station = models.ForeignKey(FireStation, on_delete=models.CASCADE, related_name='firefighters')
    contact_number = models.CharField(max_length=20)
    email = models.EmailField()
    date_joined = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.rank} {self.first_name} {self.last_name}"


class FireTruck(models.Model):
    TRUCK_TYPES = [
        ('PUMPER', 'Pumper Truck'),
        ('LADDER', 'Ladder Truck'),
        ('RESCUE', 'Rescue Truck'),
        ('TANKER', 'Tanker Truck'),
    ]

    truck_number = models.CharField(max_length=20, unique=True)
    truck_type = models.CharField(max_length=20, choices=TRUCK_TYPES)
    station = models.ForeignKey(FireStation, on_delete=models.CASCADE, related_name='trucks')
    capacity = models.IntegerField(help_text="Water capacity in gallons")
    status = models.CharField(max_length=20, default='Available')
    last_maintenance = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.truck_type} - {self.truck_number}"


class WeatherCondition(models.Model):
    station = models.ForeignKey(FireStation, on_delete=models.CASCADE, related_name='weather_conditions')
    temperature = models.FloatField()
    humidity = models.FloatField()
    wind_speed = models.FloatField()
    wind_direction = models.CharField(max_length=20)
    precipitation = models.FloatField()
    weather_description = models.CharField(max_length=100)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Weather at {self.station.name} - {self.recorded_at}"
