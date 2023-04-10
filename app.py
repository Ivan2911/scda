import requests
import json
from datetime import datetime
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium

# API keys
OPENWEATHERMAP_API_KEY = 'your_openweathermap_api_key'
OPENEI_API_KEY = 'your_openei_api_key'
OPENROUTESERVICE_API_KEY = 'your_openrouteservice_api_key'
FLIGHTAWARE_API_KEY = 'your_flightaware_api_key'
MARINETRAFFIC_API_KEY = 'your_marinetraffic_api_key'

# Supplier locations (coordinates)
SUPPLIER_LOCATIONS = [
    {"id": "supplier_1", "coordinates": [38.8951100, -77.0363700]},
    {"id": "supplier_2", "coordinates": [34.052235, -118.243683]}
]

# Fetch weather data
def get_weather_data(coordinates):
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={coordinates[0]}&lon={coordinates[1]}&appid={OPENWEATHERMAP_API_KEY}'
    response = requests.get(url)
    return response.json()

# Fetch power outage data
def get_power_outage_data():
    url = f'https://utilityapi.com/api/v2/outages?access_token={OPENEI_API_KEY}'
    response = requests.get(url)
    return response.json()

# Fetch routing data
def get_routing_data(coordinates_1, coordinates_2):
    url = f'https://api.openrouteservice.org/v2/directions/driving-car?api_key={OPENROUTESERVICE_API_KEY}&start={coordinates_1[1]},{coordinates_1[0]}&end={coordinates_2[1]},{coordinates_2[0]}'
    response = requests.get(url)
    return response.json()

# Fetch air shipment data
def get_air_shipment_data():
    url = f'https://flightxml.flightaware.com/json/FlightXML2/Search?query=origin&howMany=15&offset=0&apiKey={FLIGHTAWARE_API_KEY}'
    response = requests.get(url)
    return response.json()

# Fetch port traffic data
def get_port_traffic_data(coordinates):
    url = f'https://services.marinetraffic.com/api/exportvessel/v:8/{MARINETRAFFIC_API_KEY}/timespan:60/protocol:jsono/center_point:{coordinates[1]},{coordinates[0]}/radius:10'
    response = requests.get(url)
    return response.json()

def analyze_data():
    disruption_risk = []

    # Loop through supplier locations
    for supplier in SUPPLIER_LOCATIONS:
        weather_data = get_weather_data(supplier['coordinates'])
        port_traffic_data = get_port_traffic_data(supplier['coordinates'])

        # Calculate disruption risk based on weather, port traffic, etc.
        risk_score = calculate_risk_score(weather_data, port_traffic_data)
        disruption_risk.append({
            "supplier_id": supplier["id"],
            "coordinates": supplier["coordinates"],
            "risk_score": risk_score
        })

    return disruption_risk

# Calculate risk score based on weather, port traffic, etc.
def calculate_risk_score(weather_data, port_traffic_data):
    risk_score = 0

    # Weather risk
    if weather_data["weather"][0]["main"] in ["Thunderstorm", "Rain", "Snow"]:
        risk_score += 1

    # Port traffic risk
    if len(port_traffic_data) > 10:
        risk_score += 1

    return risk_score

# Display results in a dashboard or report
def display_results(disruption_risk):
    # Create a GeoDataFrame
    geometry = [Point(xy) for xy in [x["coordinates"] for x in disruption_risk]]
    gdf = gpd.GeoDataFrame(disruption_risk, geometry=geometry)

    # Generate an interactive map
    m = folium.Map(location=[38.8951100, -77.0363700], zoom_start=4)

    # Add supplier markers with risk score
    for index, row in gdf.iterrows():
        color = "green" if row["risk_score"] == 0 else "orange" if row["risk_score"] == 1 else "red"
        folium.Marker(location=[row["coordinates"][0], row["coordinates"][1]], popup=f'Supplier ID: {row["supplier_id"]}<br>Risk Score: {row["risk_score"]}', icon=folium.Icon(color=color)).add_to(m)

    return m

# Main function
def main():
    disruption_risk = analyze_data()
    dashboard = display_results(disruption_risk)
    dashboard.save("dashboard.html")

if __name__ == "__main__":
    main()


