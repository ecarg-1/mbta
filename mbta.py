import requests, datetime, os
from dotenv import load_dotenv
def _get_directions() -> dict:
    destinations = dict()
    url = f'{base_url}/routes'
    params = {'filter[type]': '0,1'}                                    #type attribute: 0 for light rail, 1 for heavy  rail
    routes = requests.get(url, headers=headers, params=params).json()
    for x in routes['data']:
        direction_names = x['attributes']['direction_names']
        direction_destinations = x['attributes']['direction_destinations']
        d_dict = {x[0] : x[1] for x in zip(direction_names, direction_destinations)}
        stop_id = x['id']
        destinations[stop_id] = d_dict
    return destinations

def _get_route_ids() -> dict:
    url = f'{base_url}/routes'
    params = {'filter[type]': '0,1'}                                    #type attribute: 0 for light rail, 1 for heavy  rail
    routes = requests.get(url, headers=headers, params=params).json()
    route_ids = [x['id'] for x in routes['data']]
    return {route_id : _get_stop_names_on_route(route_id) for route_id in route_ids}

def _get_stop_names_on_route(route:str) -> list:
    url = f'{base_url}/stops'
    params = {'filter[route]':route}
    stops = requests.get(url, headers=headers, params=params).json()
    names =  [x['attributes']['name'] for x in stops['data']]
    return names

def _get_stop_id(stop_name:str):
    id_dict = dict()
    url = f'{base_url}/stops'
    ids = requests.get(url, headers=headers).json()
    for id in ids['data']: 
        if id['attributes']['name'] == stop_name and id['attributes']['vehicle_type'] in [0,1]:
            id_dict[id['attributes']['description']] = id['id']
    return id_dict

def display_lines(): 
    for line in routes.keys(): print(line)

def display_stations(line): 
    for stop in routes[line]: print(stop)

def display_directions(): 
    for k, v in directions.items():
        print('Line:', k)
        for direction_name in v.keys():
            print('\tDirection:', direction_name, '\tDestination:', v[direction_name])

def help():
    print('To get predictions, call the get_predictions(line, direction_name, station) function.\nThe parameters are the line, direction name, and the station.\nIf you are unsure of the names of any of these parameters, you can call display_lines(), display_directions() or display_stations(line_name)')

def get_predictions(line:str, direction_name:str, station:str):
    direction_destination = directions[line][direction_name]
    other_direction = 'North' if direction_name == 'East' else direction_name
    stop_ids =  _get_stop_id(station)
    for d in stop_ids.keys():
        if direction_name in d or direction_destination in d or other_direction in d: stop_id = stop_ids[d]
    url = f'{base_url}/predictions?filter[stop]={stop_id}'
    x = requests.get(url, headers = headers).json()
    ct = 0
    for p in x['data']: 
        if ct >= display_trains: break
        arrival_time_as_is = p['attributes']['arrival_time']
        if arrival_time_as_is:                          #prevents errors if the train was schedule_relationship = SKIPPED meaning the arrival time would be None
            arrival_time = arrival_time_as_is[11:19]
        else: continue
        train = p['relationships']['route']['data']['id']
        hr, mins, sec = int(arrival_time[0:2]), int(arrival_time[3:5]), int(arrival_time[6:])
        at = datetime.datetime.combine(datetime.date.today(), datetime.time(hr, mins, sec))
        now = datetime.datetime.now()
        difference = str(at - now)[2:4]
        if not difference.isnumeric(): continue
        direction = directions[train][direction_name]
        print(train, direction,':',arrival_time,'in', difference, 'mins')
        ct += 1

load_dotenv()
api_key = os.environ.get('api_key')
base_url = 'https://api-v3.mbta.com'
headers = {'X-API-Key': api_key, 'accept':'application/json'}
display_trains = 4
routes = _get_route_ids()
directions = _get_directions()
