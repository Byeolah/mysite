from django.db import models


# Trip Class - the most important one.
class Trip(models.Model):
    name = models.CharField(max_length=100, blank=False)
    country = models.CharField(max_length=50, blank=False)
    city = models.CharField(max_length=50, blank=True)
    departure_date = models.DateField(blank=False)
    comeback_date = models.DateField(blank=False)
    target = models.CharField(max_length=50, blank=False)

    def __str__(self):
        return self.name




