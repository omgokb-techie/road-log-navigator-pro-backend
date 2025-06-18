from django.urls import path
from .views import TripRouteView

urlpatterns = [
    path('route/', TripRouteView.as_view(), name='trip-route'),
]