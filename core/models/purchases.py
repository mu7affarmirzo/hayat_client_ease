from django.db import models


class Booking(models.Model):
    series = models.CharField(max_length=255, blank=True, null=True)
