
import requests
import json
import datetime as dt
import os
from dotenv import load_dotenv

def add_hours(time_input, hours):
    new_time = dt.datetime.strptime(time_input, "%Y-%m-%dT%H:%M:%SZ")
    return str(new_time + dt.timedelta(hours=hours))


# lat, long ja list väärtustest + headerist väärtused
def trim_json(input_json, header):
    new_json = {}
    series = []
    for item in input_json['properties']['timeseries']:
        if add_hours(item['time'], 2).startswith(dt.datetime.today().strftime('%Y-%m-%d')):
            #print(item['time'])
            time = add_hours(item['time'], 2)
            air_temperature = item['data']['instant']['details']['air_temperature']
            wind_speed = item['data']['instant']['details']['wind_speed']
            symbol_code = item['data']['next_1_hours']['summary']['symbol_code']
            precipitation_amount = item['data']['next_1_hours']['details']['precipitation_amount']
            series.append(
                {
                    'time': time,
                    'air_temperature': air_temperature,
                    'wind_speed': wind_speed,
                    'symbol_code': symbol_code,
                    'precipitation_amount': precipitation_amount,
                }
            )

    new_json['lat'] = input_json['geometry']['coordinates'][1]
    new_json['lon'] = input_json['geometry']['coordinates'][0]
    new_json['expires'] = header['Expires']
    new_json['last_modified'] = header['Last-Modified']
    new_json['timeseries'] = series

    return new_json


def request_to_yrno(lat, lon, existing_data = None):
    print("Requesting weather from YRNO")
    url = "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=" + str(lat) + "&lon=" + str(lon)

    load_dotenv()
    sitename = "Ilmataat/1.0 (https://github.com/pert6000/ilmataat; " + os.environ["USER_AGENT_EMAIL"] + ")"

    headers = {
        "User-Agent": sitename,
    }

    if existing_data is not None:
        headers["If-Modified-Since"] = existing_data['last_modified']


    response = requests.get(url, headers=headers)

    #print(response.status_code)
    #print(response.json())
    #print(response.headers)

    if response.status_code == 304:
        print("Data not modified")
        existing_data['expires'] = response.headers['Expires']
    elif response.status_code == 200:
        print("Data retrieved")
        existing_data = trim_json(response.json(), response.headers)
    else:
        print("Something went wrong, HTTP status code: " + str(response.status_code))

    return existing_data


def weather_data(lat, lon):
    # vaatab faili kas seal on kanne selliste pikkus/laiuskraadidega mis ei ole expired
    # kui on siis tagastab selle

    with open('data.json', 'r', encoding='utf-8') as f:
        print("Reading weather data from data.json")
        data = json.load(f)

    existing_entry = {}

    for entry in data['data']:
        if entry['lat'] == lat and entry['lon'] == lon:
            print("Found an existing entry with these coordinates")
            existing_entry = entry

    if existing_entry == {}:
        print("No existing entry with these coordinates")
        updated_entry = request_to_yrno(lat, lon)
        data['data'].append(updated_entry)

    elif dt.datetime.strptime(existing_entry['expires'], "%a, %d %b %Y %H:%M:%S GMT") < dt.datetime.today() + dt.timedelta(hours=-3):
        print("Found an existing entry, but it is expired")
        updated_entry = request_to_yrno(lat, lon, existing_entry)
        data['data'].remove(existing_entry)
        data['data'].append(updated_entry)
    else:
        updated_entry = existing_entry

    with open('data.json', 'w', encoding='utf-8') as f:
        print("writing data to data.json")
        json.dump(data, f, ensure_ascii=False, indent=4)

    return updated_entry


def main():
    pass


#if __name__ == '__main__':
    #main()

weather_data(58, 22.2)



