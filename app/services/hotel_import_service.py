import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def import_hotels_osm(city_name: str):
    """
    Cerca hotel in una città usando OpenStreetMap (Overpass API).
    Restituisce una lista di hotel con nome, latitudine e longitudine.
    """

    query = f"""
    [out:json][timeout:25];
    area["name"="{city_name}"]["boundary"="administrative"]->.searchArea;
    (
      node["tourism"="hotel"](area.searchArea);
      node["tourism"="guest_house"](area.searchArea);
      node["tourism"="hostel"](area.searchArea);
      node["tourism"="apartment"](area.searchArea);
    );
    out center;
    """

    try:
        response = requests.get(OVERPASS_URL, params={'data': query})
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print("Errore richiesta OSM:", e)
        return None

    hotels_list = []
    for element in data.get("elements", []):
        hotels_list.append({
            "name": element.get("tags", {}).get("name", "Senza nome"),
            "lat": element.get("lat"),
            "lon": element.get("lon"),
            "type": element.get("tags", {}).get("tourism")
        })

    return hotels_list

