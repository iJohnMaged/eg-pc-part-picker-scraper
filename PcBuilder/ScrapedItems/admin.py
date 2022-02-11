from django.contrib import admin
from .models import *

# Register your models here.
site = admin.site

site.register(Store)
site.register(Category)
site.register(Component)
site.register(Build)
