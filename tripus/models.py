from django.db import models


# Create your models here.
class Trip(models.Model):
    name = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=50, blank=False)
    city = models.CharField(max_length=50, blank=True)
    departure_date = models.DateField(blank=False)
    comeback_date = models.DateField(blank=False)
    target = models.CharField(max_length=50, blank=False)