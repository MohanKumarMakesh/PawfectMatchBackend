from django.db import models
from django.contrib.auth.models import User

class Dog(models.Model):
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    image = models.URLField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dogs')
    def __str__(self):
        return str(self.name)


objects = models.Manager()  # Add default manager
