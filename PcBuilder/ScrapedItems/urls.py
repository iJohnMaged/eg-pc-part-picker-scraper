from django.urls import path, include
from rest_framework import routers
from .views import ComponentViewset, create_build, BuildViewset

router = routers.DefaultRouter()
router.register(r"components", ComponentViewset)
router.register(r"builds", BuildViewset)

urlpatterns = [
    path("", include(router.urls)),
    path("create-build/", create_build, name="create_build"),
]
