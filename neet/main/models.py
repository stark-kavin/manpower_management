from django.db import models
from django.contrib.auth.models import User

class Center(models.Model):
    name = models.CharField(max_length=100)
    map = models.TextField(blank=True, null=True)
    count = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
class Operator(models.Model):
    name = models.CharField(max_length=100)
    center = models.ForeignKey(Center, on_delete=models.SET_NULL, related_name='operators', blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='operators_created', blank=True, null=True)

    def __str__(self):
        return self.name