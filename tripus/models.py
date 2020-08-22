from django.db import models
from django.conf import settings
from django_countries.fields import CountryField


# Trip Class - the most important one.
class Trip(models.Model):
    name = models.CharField(max_length=100, blank=False)
    country = CountryField(null=True)
    city = models.CharField(max_length=50, blank=True)
    departure_date = models.DateField(blank=False)
    comeback_date = models.DateField(blank=False)
    target = models.CharField(max_length=50, blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


# Spending Class – how much money user spent on the trip.
class Spending(models.Model):
    name = models.CharField(max_length=200, blank=False)
    price = models.DecimalField(max_digits=15, decimal_places=2, blank=False)
    currency_code = models.CharField(max_length=3, blank=False)
    date = models.DateField()
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# Visit Class - places to visit
class Visit(models.Model):
    name = models.CharField(max_length=300, blank=False)
    category = models.CharField(max_length=50, blank=False, null=True)
    visit_date = models.DateField(null=True, blank=True)
    website = models.URLField(max_length=400, blank=True)
    address = models.CharField(max_length=500, blank=True)
    approach = models.CharField(max_length=800, blank=True)
    notes = models.CharField(max_length=1000, blank=True)
    visited = models.BooleanField(blank=False, default=False)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# Note Class - user's notes on the trip
class Note(models.Model):
    text = models.fields.TextField()
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)

    def __str__(self):
        return self.text
