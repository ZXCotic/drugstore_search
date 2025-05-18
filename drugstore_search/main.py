import requests
import sys
from io import BytesIO
from PIL import Image

GEOCODER_API_SERVER = "https://geocode-maps.yandex.ru/1.x/"
STATIC_API_SERVER = "https://static-maps.yandex.ru/v1"
SEARCH_API_SERVER = "https://search-maps.yandex.ru/v1"

GEOCODER_API_KEY = "your-geocoder-api-key"
STATIC_API_KEY = "your-static-api-key"
SEARCH_API_KEY = "your-search-api-key"


def get_response(url, params):
    """Generic function to handle API requests."""
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def get_geocoder_response(toponym):
    params = {
        "apikey": GEOCODER_API_KEY,
        "geocode": toponym,
        "format": "json"
    }
    return get_response(GEOCODER_API_SERVER, params)


def get_search_response(coords):
    params = {
        "apikey": SEARCH_API_KEY,
        "text": "аптека",
        "lang": "ru_RU",
        "ll": coords,
        "type": "biz"
    }
    return get_response(SEARCH_API_SERVER, params)


def get_static_response(coords, org_coords):
    params = {
        "maptype": "map",
        "apikey": STATIC_API_KEY,
        "pt": f'{coords},round~{org_coords},pm2dgl'
    }
    return requests.get(STATIC_API_SERVER, params=params).content


def format_hours(hours):
    """Format the working hours of the organization."""
    if "TwentyFourHours" in hours[0]:
        return "Работает круглосуточно"
    else:
        interval = hours[0]["Intervals"][0]
        return f"Работает с {interval['from'][:-3]} до {interval['to'][:-3]}"


def main():
    toponym = " ".join(sys.argv[1:])
    geocoder_response = get_geocoder_response(toponym)

    main_toponym = geocoder_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    main_toponym_coords = ",".join(main_toponym["Point"]["pos"].split(" "))
    
    search_response = get_search_response(main_toponym_coords)
    organization = search_response["features"][0]
    
    org_name = organization["properties"]["CompanyMetaData"]["name"]
    org_address = organization["properties"]["CompanyMetaData"]["address"]
    org_hours = format_hours(organization["properties"]["CompanyMetaData"]["Hours"]["Availabilities"])
    
    org_point = organization["geometry"]["coordinates"]
    org_coords = f"{org_point[0]},{org_point[1]}"
    
    static_response = get_static_response(main_toponym_coords, org_coords)
    Image.open(BytesIO(static_response)).show()
    
    print(f"{org_address}, {org_name}, {org_hours}")


if __name__ == "__main__":
    main()
