# trip/utils.py

import math

def generate_route_plan(trip):
    # Dummy values for now; integrate real API later
    avg_speed = 50  # mph
    total_distance = 1200  # miles (simulate)
    total_hours = total_distance / avg_speed

    # ELD Rule: 11 hours driving max per day
    daily_drive_limit = 11
    num_days = math.ceil(total_hours / daily_drive_limit)

    stops = []
    hours_accumulated = 0
    for day in range(num_days):
        day_hours = min(daily_drive_limit, total_hours - hours_accumulated)
        stops.append({
            "day": day + 1,
            "hours": day_hours,
            "location": f"Stop {day + 1}"
        })
        hours_accumulated += day_hours

    # Fuel every 1000 miles
    fuel_stops = []
    if total_distance > 1000:
        fuel_stops.append("Fuel Stop at ~1000 miles")

    return {
        "total_hours": total_hours,
        "stops": stops,
        "fuel_stops": fuel_stops,
        "total_distance": total_distance,
    }

def generate_eld_logs(total_hours):
    # Simulate logs across days
    daily_limit = 11
    logs = []
    hours_remaining = total_hours
    day = 1

    while hours_remaining > 0:
        driving = min(daily_limit, hours_remaining)
        off_duty = 24 - driving
        logs.append({
            "day": day,
            "driving_hours": driving,
            "off_duty_hours": off_duty,
            "graph": generate_log_graph(driving)
        })
        hours_remaining -= driving
        day += 1

    return logs

def generate_log_graph(driving_hours):
    # Simulated hourly chart (24 slots)
    # 'D' = Driving, 'O' = Off-duty
    graph = []
    for i in range(24):
        if i < driving_hours:
            graph.append("D")
        else:
            graph.append("O")
    return graph
