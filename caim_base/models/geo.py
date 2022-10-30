from django.contrib.gis.db.models import PointField
from django.db import models


class ZipCode(models.Model):
    zip_code = models.CharField(max_length=16, unique=True)
    geo_location = PointField()
