# ELD Log Project Backend

## Purpose

This backend service provides route planning and ELD (Electronic Logging Device) log generation for truck drivers.  
It receives trip details (current location, pickup, dropoff, and current cycle used) and returns:

- Route instructions and summary (distance, duration)
- Suggested fuel and rest stops
- Daily ELD log sheets, including driver status and odometer readings

The backend is designed to work with a frontend that visualizes routes and logs, helping drivers comply with HOS (Hours of Service) regulations.

---

## Features

- Calculates routes using the OSRM API
- Generates realistic fuel and rest stops based on trip distance
- Produces daily ELD logs in a format suitable for frontend display

---

## Installation

1. **Clone the repository**
   ```sh
   git clone https://github.com/omgokb-techie/road-log-navigator-pro-backend.git
   cd road-log-navigator-pro-backend
   ```

2. **Create and activate a virtual environment**
   ```sh
   python -m venv venv
   venv\Scripts\activate   # On Windows
   # source venv/bin/activate   # On macOS/Linux
   ```

3. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Install additional dependencies**
   - Django
   - djangorestframework
   - django-cors-headers
   - requests

   If not in `requirements.txt`, install manually:
   ```sh
   pip install django djangorestframework django-cors-headers requests
   ```

5. **Apply migrations**
   ```sh
   python manage.py migrate
   ```

6. **Run the development server**
   ```sh
   python manage.py runserver
   ```

---

## API Usage

- **Endpoint:** `POST /api/trip/route/`
- **Request Body:**  
  ```json
  {
    "currentLocation": { ... },
    "pickupLocation": { ... },
    "dropoffLocation": { ... },
    "currentCycleUsed": 0
  }
  ```
  (Locations follow GeoJSON Feature structure.)

- **Response:**  
  Returns route summary, stops, and ELD logs.

---

## Notes

- Make sure to enable CORS for your frontend origin in `settings.py` using `django-cors-headers`.
- The backend uses the public OSRM API for routing; for production, consider hosting your own routing service.
