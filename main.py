import os
import json
import requests
from dotenv import load_dotenv
from geopy import distance
import folium

load_dotenv()
API_KEY = os.getenv('API_KEY')

def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return float(lon), float(lat)
def get_user_posts(new_coffee_data):
    return new_coffee_data['Distance_to_User_km']

def main():
    with open("coffee.json", "r", encoding="CP1251") as my_file:
        coffee_data = my_file.read()
        coffee = json.loads(coffee_data)

    new_coffee_data = []

    city_user = input('Где вы находитесь? ')
    coords = fetch_coordinates(API_KEY, city_user)

    for coffee in coffee:
        coffee_name = coffee['Name']
        coffee_longitude = coffee['Longitude_WGS84']
        coffee_latitude = coffee['Latitude_WGS84']

        coffee_coords = (coffee_longitude, coffee_latitude)
        dist = distance.distance(coords, coffee_coords).km

        data_coffee_new = {
            'Name': coffee_name,
            'Longitude': coffee_longitude,
            'Latitude': coffee_latitude,
            'Distance_to_User_km': dist
        }
        new_coffee_data.append(data_coffee_new)

    five_coffee = sorted(new_coffee_data, key=lambda x: x['Distance_to_User_km'])[:5]

    map_center = (coords[1], coords[0])  # Широта, Долгота
    coffee_map = folium.Map(location=map_center, zoom_start=14)

    for coffee in five_coffee:
        folium.Marker(
            location=(coffee['Latitude'], coffee['Longitude']),
            popup=f"{coffee['Name']}<br>Расстояние: {coffee['Distance_to_User_km']:.2f} км",
            icon=folium.Icon(color='blue')
        ).add_to(coffee_map)

        coffee_map.save("coffee_map.html")


if __name__ == '__main__':
   main()