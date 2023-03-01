from django.db import models

# Create your models here.
from django.db import models

class GeneratedName(models.Model):
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10)
    nationality = models.CharField(max_length=255)
    meaning = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
