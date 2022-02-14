from rest_framework import serializers
from django.db import models
from .models import *


class CateogrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = "__all__"


class ComponentListSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        iterable = data.all() if isinstance(data, models.Manager) else data
        stores_map = {}
        for item in iterable:
            rep = self.child.to_representation(item)
            if rep["store"]["name"] in stores_map:
                stores_map[rep["store"]["name"]].append(rep)
            else:
                stores_map[rep["store"]["name"]] = [rep]
        return [{"label": key, "options": value} for key, value in stores_map.items()]


class ComponentSerializer(serializers.ModelSerializer):
    category = CateogrySerializer(read_only=True)
    store = StoreSerializer(read_only=True)

    class Meta:
        model = Component
        fields = "__all__"
        list_serializer_class = ComponentListSerializer


class BuildSerializer(serializers.ModelSerializer):
    components = ComponentSerializer(many=True, read_only=True)

    class Meta:
        model = Build
        fields = "__all__"
