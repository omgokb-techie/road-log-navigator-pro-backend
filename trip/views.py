import requests
from datetime import datetime, timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class TripRouteView(APIView):
    def post(self, request):
        current = request.data.get("currentLocation")      # [lon, lat]
        pickup = request.data.get("pickupLocation")        # [lon, lat]
        dropoff = request.data.get("dropoffLocation")      # [lon, lat]

        if not all([current, pickup, dropoff]):
            return Response({"error": "Missing coordinates"}, status=400)

        try:
            route = self.fetch_osrm_route([
                current['geometry']['coordinates'],
                pickup['geometry']['coordinates'],
                dropoff['geometry']['coordinates']
            ])
            if not route:
                return Response({"error": "Routing failed"}, status=500)

            total_distance_km = route["distance"] / 1000
            total_duration_hrs = route["duration"] / 3600
            total_distance_miles = total_distance_km * 0.621371

            # Build stops
            fuel_stops = self.generate_fuel_stops(total_distance_miles)
            rest_stops = self.generate_rest_stops(total_distance_miles)

            # Build logs
            logs = self.generate_eld_logs(
                total_distance_miles, total_duration_hrs,
                request.data.get("currentLocation", "Current Location"),
                request.data.get("pickupLocation", "Pickup Location"),
                request.data.get("dropoffLocation", "Dropoff Location")
            )

            return Response({
                "route": {
                    "distance": round(total_distance_miles),
                    "duration": round(total_duration_hrs, 1),
                    "fuelStops": fuel_stops,
                    "restStops": rest_stops
                },
                "logs": logs
            })

        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def fetch_osrm_route(self, coordinates):
        coord_str = ";".join([f"{lon},{lat}" for lon, lat in coordinates])
        url = f"http://router.project-osrm.org/route/v1/driving/{coord_str}?overview=false"
        res = requests.get(url)
        if res.status_code != 200:
            return None
        route = res.json()["routes"][0]
        return route

    def generate_fuel_stops(self, total_miles):
        fuel_stops = []
        fuel_points = [m for m in range(0, int(total_miles), 1000)][1:]
        for i, mile in enumerate(fuel_points):
            fuel_stops.append({
                "name": f"Fuel Stop {i + 1}",
                "location": f"Highway Mile {mile}",
                "distanceFromStart": mile
            })
        return fuel_stops

    def generate_rest_stops(self, total_miles):
        rest_stops = []
        rest_points = [m for m in range(250, int(total_miles), 500)]
        for i, mile in enumerate(rest_points):
            rest_stops.append({
                "location": f"Rest Area Mile {mile}",
                "type": "break" if i % 2 == 0 else "rest",
                "duration": 0.5 if i % 2 == 0 else 10,
                "distanceFromStart": mile
            })
        return rest_stops

    def generate_eld_logs(self, total_miles, total_hours, current_loc, pickup_loc, dropoff_loc):
        
        avg_speed = 50  
        odo = 123456
        logs_per_day = []
        miles_remaining = total_miles
        hours_remaining = total_hours
        day_index = 0

        while hours_remaining > 0 and miles_remaining > 0:
            driving_hours_today = min(hours_remaining, 9)  # allow max 9h drive/day
            driving_segments = [4.5, driving_hours_today - 4.5] if driving_hours_today > 4.5 else [driving_hours_today]
            current_time = datetime.strptime("06:00", "%H:%M")
            date = (datetime.now() + timedelta(days=day_index)).strftime("%Y-%m-%d")
            logs = []

            # 1. On-duty (pre-trip)
            logs.append({
                "time": current_time.strftime("%H:%M"),
                "status": "on-duty",
                "location": current_loc if day_index == 0 else "Truck Stop",
                "odometer": odo
            })

            current_time += timedelta(minutes=30)

            # Driving segments
            for i, segment in enumerate(driving_segments):
                miles_driven = int(segment * avg_speed)
                odo += miles_driven

                logs.append({
                    "time": current_time.strftime("%H:%M"),
                    "status": "driving",
                    "location": f"Highway Mile {int(total_miles - miles_remaining + miles_driven)}",
                    "odometer": odo
                })

                current_time += timedelta(hours=segment)
                miles_remaining -= miles_driven
                hours_remaining -= segment

                if i == 0 and len(driving_segments) > 1:
                    # Add 30-min break after first 4.5h
                    logs.append({
                        "time": current_time.strftime("%H:%M"),
                        "status": "off-duty",
                        "location": "Rest Stop",
                        "odometer": odo
                    })
                    current_time += timedelta(minutes=30)

            # On-duty post-trip (1 hour)
            logs.append({
                "time": current_time.strftime("%H:%M"),
                "status": "on-duty",
                "location": "Fuel Stop" if miles_remaining > 0 else dropoff_loc,
                "odometer": odo
            })

            current_time += timedelta(hours=1)

            # Sleeper (overnight)
            logs.append({
                "time": current_time.strftime("%H:%M"),
                "status": "sleeper",
                "location": "Truck Stop" if miles_remaining > 0 else dropoff_loc,
                "odometer": odo
            })

            # Accumulate daily log
            logs_per_day.append({
                "date": date,
                "driverName": "John Doe",
                "truckNumber": "TRK001",
                "logs": logs,
                "totalDriving": round(driving_hours_today, 1),
                "totalOnDuty": round(driving_hours_today + 1.5, 1)
            })

            day_index += 1

        return logs_per_day
