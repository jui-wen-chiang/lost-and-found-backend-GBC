from rest_framework import generics
from api.models import Location
from api.serializers import LocationSerializer

class LocationListView(generics.ListAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer