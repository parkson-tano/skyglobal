from django.db import models

# Create your models here.

class Flight(models.Model):
    from_airport = models.CharField(max_length=256)
    to_airport = models.CharField(max_length=256)
    departure_date = models.DateField()
    return_date = models.DateField()
    travel_type = models.CharField(max_length=256)
    adult = models.IntegerField()
    children = models.IntegerField()
    infants = models.IntegerField()