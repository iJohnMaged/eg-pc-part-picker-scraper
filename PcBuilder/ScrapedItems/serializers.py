from rest_framework import serializers
from .models import *


class CateogrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = "__all__"


class ComponentSerializer(serializers.ModelSerializer):
    category = CateogrySerializer(read_only=True)
    store = StoreSerializer(read_only=True)

    class Meta:
        model = Component
        fields = "__all__"


class BuildSerializer(serializers.ModelSerializer):
    components = ComponentSerializer(many=True, read_only=True)

    class Meta:
        model = Build
        fields = "__all__"
