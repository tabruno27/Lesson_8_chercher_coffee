import os
import json
import requests
from dotenv import load_dotenv
from geopy import distance
from pprint import pprint
import folium


with open("coffee.json", "r", encoding="CP1251") as my_file:
    coffee_data = my_file.read()
coffee = json.loads(coffee_data)

new_coffee_data = []

load_dotenv()
apikey = os.getenv('API_KEY')

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


city_user = input('Где вы находитесь? ')
coords = fetch_coordinates(apikey, city_user)
print(f'Ваши координаты: {coords}')


for coffee in coffee:
    coffee_name = coffee['Name']
    coffee_longitude = coffee['Longitude_WGS84']
    coffee_latitude = coffee['Latitude_WGS84']

    coffee_coords = (coffee_longitude, coffee_latitude)  # Широта, Долгота
    dist = distance.distance(coffee_coords, coords).km  # Расстояние в километрах

    data_coffee_new = {
        'Name': coffee_name,
        'Longitude': coffee_longitude,
        'Latitude': coffee_latitude,
        'Distance_to_User_km': dist
    }
    new_coffee_data.append(data_coffee_new)

def get_user_posts(new_coffee_data):
    return new_coffee_data['Distance_to_User_km']


five_coffee = sorted(new_coffee_data, key=lambda x: x['Distance_to_User_km'])[:5]

pprint(five_coffee, sort_dicts=False)

map_center = (coords[1], coords[0])  # Широта, Долгота
coffee_map = folium.Map(location=map_center, zoom_start=14)

if __name__ == '__main__':
    for coffee in five_coffee:
        folium.Marker(
            location=(coffee['Latitude'], coffee['Longitude']),
            popup=f"{coffee['Name']}<br>Расстояние: {coffee['Distance_to_User_km']:.2f} км",
            icon=folium.Icon(color='blue')
        ).add_to(coffee_map)

        coffee_map.save("coffee_map.html")
