import json
from django.http import HttpResponseNotAllowed, JsonResponse
from rest_framework import viewsets
from .models import Component, Category, Build
from .serializers import ComponentSerializer
from rest_framework.exceptions import NotAcceptable
from django.views.decorators.csrf import csrf_exempt


class ComponentViewset(viewsets.ModelViewSet):
    queryset = Component.objects.all()
    serializer_class = ComponentSerializer

    def get_queryset(self):
        category_name = self.request.query_params.get("category_name", None)
        if category_name is None:
            raise NotAcceptable("category_name is required")
        try:
            category = Category.objects.get(name__iexact=category_name)
        except Category.DoesNotExist:
            raise NotAcceptable("category_name does not exist")

        return Component.objects.filter(recently_scraped=True, category=category)


@csrf_exempt
def create_build(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    # parse request body as JSON
    try:
        data = request.body.decode("utf-8")
        data = json.loads(data)
    except:
        return JsonResponse({"detail": "invalid request body"}, status=400)
    print(type(data))
    print(data)

    if "components" not in data:
        return JsonResponse({"detail": "components is required"}, status=400)

    components = data["components"]
    if not isinstance(components, list):
        return JsonResponse({"detail": "components must be a list"}, status=400)

    if len(components) == 0:
        return JsonResponse({"detail": "components must not be empty"}, status=400)

    components_objs = []

    for component in components:
        if "id" not in component:
            return JsonResponse({"detail": "component id is required"}, status=400)
        try:
            component = Component.objects.get(id=component["id"])
            components_objs.append(component)
        except Component.DoesNotExist:
            return JsonResponse({"detail": "component does not exist"}, status=400)

    build = Build.objects.create()
    build.components.set(components_objs)
    build.save()

    return JsonResponse({"id": str(build.id)}, status=201)
