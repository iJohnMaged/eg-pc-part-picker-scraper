import uuid
from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.TextField(unique=True)


class Store(models.Model):
    name = models.TextField()
    url = models.TextField()

    class Meta:
        unique_together = ("name", "url")


class Component(models.Model):
    name = models.TextField()
    image = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    url = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    recently_scraped = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("name", "store", "category")
        ordering = ("-created_at",)


class Build(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(null=True)
    components = models.ManyToManyField(Component)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
