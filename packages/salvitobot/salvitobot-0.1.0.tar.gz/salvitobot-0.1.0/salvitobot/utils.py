import datetime
import os

import dataset
import pytz
import sqlalchemy

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

            obj['datetime_utc'] = datetime.datetime.fromtimestamp(obj['time'] / 1000, pytz.utc)

            out = "SISMO"
            out += ". " + str(obj['magnitude']) + " grados " + obj['magnitude_type']
            out += " en " + obj['place']
            out += ". A horas "
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
        table = db.create_table("salvitobot")
        table.create_column('code', sqlalchemy.String)  # unique identifier of earthquake
        table.create_column('url', sqlalchemy.String)
        table.create_column('tweet', sqlalchemy.String)
        table.create_column('blogpost', sqlalchemy.Text)
        table.create_column('twitter_user', sqlalchemy.String)
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
    return this_string
