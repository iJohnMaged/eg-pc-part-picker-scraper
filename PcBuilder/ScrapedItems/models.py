from enum import unique
from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

class Store(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField()
    
    class Meta:
        unique_together = ('name', 'url')

class Component(models.Model):
    name = models.CharField(max_length=100)
    image = models.URLField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    url = models.URLField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    recently_scraped = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'store', 'category')
        ordering = ('-created_at',)