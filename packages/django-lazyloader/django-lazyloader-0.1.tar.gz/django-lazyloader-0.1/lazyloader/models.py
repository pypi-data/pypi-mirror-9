from django.db import models


class DemoObject(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    stock = models.BooleanField()
    price = models.CharField(max_length=255)