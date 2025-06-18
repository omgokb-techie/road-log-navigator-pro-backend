from rest_framework import serializers

class GeometrySerializer(serializers.Serializer):
    type = serializers.CharField()
    coordinates = serializers.ListField(child=serializers.FloatField())

class LocationFeatureSerializer(serializers.Serializer):
    type = serializers.CharField()
    properties = serializers.DictField()
    geometry = GeometrySerializer()

class TripDataSerializer(serializers.Serializer):
    currentLocation = LocationFeatureSerializer()
    pickupLocation = LocationFeatureSerializer()
    dropoffLocation = LocationFeatureSerializer()
    currentCycleUsed = serializers.FloatField()