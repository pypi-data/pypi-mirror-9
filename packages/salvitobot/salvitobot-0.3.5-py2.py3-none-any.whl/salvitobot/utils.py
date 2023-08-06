import datetime
import os
import re

import arrow
import dataset
import pytz
import requests

from . import config


def parse_quake_data(data, country):
    """Extract info about earthquake.

    Args:
        ``data``: dict object as downloaded from web service.
        ``country``: string, country to look for earthquake for

    Returns:
        list of earthquakes.

    """
    quakes = []
    country = country.lower()
    for i in data['features']:
        place = i['properties']['place']
        if country in place.lower():
            obj = dict()
            obj['country'] = country
            obj['detail'] = i['properties']['detail']
            obj['code'] = i['properties']['code']
            obj['magnitude'] = i['properties']['mag']
            obj['magnitude_type'] = i['properties']['magType']

            # tz: timezone, Timezone offset from UTC in minutes
            obj['tz'] = i['properties']['tz']
            obj['type'] = i['properties']['type']

            obj['link'] = i['properties']['url']
            obj['place'] = translate_string(i['properties']['place'])
            obj['time'] = i['properties']['time']
            obj['longitude'] = i['geometry']['coordinates'][0]
            obj['latitude'] = i['geometry']['coordinates'][1]
            # depth is in km
            obj['depth'] = i['geometry']['coordinates'][2]

            utc = arrow.get(datetime.datetime.fromtimestamp(obj['time'] / 1000, pytz.utc))
            obj['datetime_utc'] = utc.datetime

            local = utc.replace(minutes=obj['tz'])
            obj['datetime_local'] = local.datetime

            out = "SISMO"
            out += ". " + str(obj['magnitude']) + " grados " + str(obj['magnitude_type']).capitalize()
            out += " a " + obj['place']
            out += ". A horas " + datetime.datetime.strftime(obj['datetime_local'], '%H:%M')
            out += " del " + datetime.datetime.strftime(obj['datetime_local'], '%d %b')
            out += " " + obj['link']

            obj['tuit'] = out
            quakes.append(obj)
    return quakes


def create_database(test=None):
    """
    Creates a sqlite3 database if not exists.

    :test: optional, creates database for testing only
    :return: database handle using ``dataset``

    """
    if test is None:
        filename = os.path.join(config.base_folder, "salvitobot.db")
    else:
        filename = os.path.join(config.base_folder, "salvitobot_test.db")

    if not os.path.isfile(filename):
        db = dataset.connect('sqlite:///' + filename)
        db.create_table("salvitobot")
    else:
        db = dataset.connect('sqlite:///' + filename)

    return db


def translate_string(this_string):
    """
    Do silly translation.

    :param this_string:
    :return: esta_cuerda

    """
    this_string = this_string.replace(' of ', ' de ')
    this_string = this_string.replace(' W ', ' O ')
    this_string = this_string.replace('NW', 'NO')
    this_string = this_string.replace('WNW', 'ONO')
    this_string = this_string.replace('SW', 'SO')
    return this_string


def save_to_db(item, test=None):
    """
    Saves quake item to local sqlite3 database.

    :param item:

    """
    db = create_database(test)
    table = db['salvitobot']
    row = table.find_one(code=item['code'])

    if row is None:
        table.insert(item)


def extract_nearby_cities(item, country):
    res = requests.get(item['detail'])
    r = res.json()

    nearby_cities_url = r['properties']['products']['nearby-cities'][0]['contents']['nearby-cities.json']['url']
    res = requests.get(nearby_cities_url)
    r = res.json()

    out = []
    append = out.append

    j = 0
    for i in r:
        city = 'a ' + str(i['distance']) + ' km al '
        city += translate_string(i['direction']) + ' de ' + i['name']
        city = city.replace(', ' + country, '')
        append(city)
        j += 1
        if j == 3:
            break

    if len(out) > 1:
        out[-1] = 'y ' + out[-1]
    nearby_cities = ', '.join(out)
    nearby_cities = re.sub(', y', ' y', nearby_cities)
    return nearby_cities
