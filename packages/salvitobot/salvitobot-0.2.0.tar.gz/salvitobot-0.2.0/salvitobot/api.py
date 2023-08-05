import codecs
from datetime import datetime
from datetime import timedelta as td
import json
import os
import re
import time

import requests

from . import config
from . import utils
from .writer import Writer
from .exceptions import NoCountryError
from .exceptions import ProcedureError


class Bot(object):
    """Main class for Salvitobot.

    This is the only contact point with users.

    Attrs:
        ``quake``: list of quake objects fetched from web service.

        ``quakes_to_write``: list of quakes that are new to our database and
                             and need to be tweeted or written about.

        ``urls``: sources to fetch data on quakes.

    """
    def __init__(self):
        self.quake = None
        self._quakes_to_write = []
        self.urls = [
            "http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_hour.geojson",
            "http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson",
        ]

    def get_quake(self, my_dict=None, country=None):
        """Gets quake info from given dict, or the web.

        Args:
            ``my_dict``: optional, dictionary based on json object from the web
                         service.

            ``country``: required, country to get earthquakes for.

        Raises:
            ``NoCountryError``: if no country is specified for this method.

        """
        if country is None:
            raise NoCountryError('You need to specify one country to get earthquakes for.')

        if my_dict is not None:
            self.quake = utils.parse_quake_data(my_dict, country=country)
        else:
            sismos_peru = []
            for url in self.urls:
                r = requests.get(url)
                data = json.loads(r.text)

                filename = os.path.join(config.base_folder, str(time.time()) + ".json")
                f = codecs.open(filename, "w", "utf-8")
                f.write(json.dumps(data, indent=4))
                f.close()

                parsed_data = utils.parse_quake_data(data, country=country)
                sismos_peru += parsed_data
            self.quake = sismos_peru

    def is_new_quake(self):
        """

        :return: ``True`` or ``False``
        """
        # Reset quakes to write
        self._quakes_to_write = []

        db = utils.create_database()
        if self.quake is None:
            # get quake function has not been called
            raise ProcedureError("You need to call the function .get_quake(country='MyCountry') first")
        elif self.quake == []:
            print("No results were found.")
            return False
        else:
            table = db['salvitobot']
            for item in self.quake:
                if table.find_one(code=item['code']) is None:
                    self._quakes_to_write.append(item)

            if len(self._quakes_to_write) > 0:
                return True
            else:
                return False

    def write_post(self, publish=None):
        """
        Write post for new quakes and publish in Wordpress.

        :param publish: True or False
        :return: text of post

        """
        if self.quake is None:
            # get quake function has not been called
            raise ProcedureError("You need to call the function .get_quake(country='MyCountry') first")
        else:
            if len(self._quakes_to_write) < 1:
                print("Nothing to do.")
            else:
                blogger = Writer()
                blogger.write_post(self._quakes_to_write, publish)


def a():
    # line is a line of downloaded data
    match = re.search("(http://.+)", tuit)
    user = re.search("(@\w+)", tuit)

    item = dict()
    item['url'] = match.groups()[0]
    item['tuit'] = tuit
    if user:
        item['twitter_user'] = user.groups()[0]

        if not table.find_one(url=item['url'], twitter_user=item['twitter_user']):
            print("DO TUIT: %s" % str(item['tuit']))
            table.insert(item)
            return "do_tuit"
        else:
            print("DONT TUIT: %s" % str(item['tuit']))
            return "dont_tuit"
    else:
        if not table.find_one(url=item['url']):
            print("DO TUIT: %s" % str(item['tuit']))
            table.insert(item)
            return "do_tuit"
        else:
            print("DONT TUIT: %s" % str(item['tuit']))
            return "dont_tuit"


def tuit(lista, debug):
    # print lista
    oauth = api.get_oauth()

    users = [
        # 'manubellido',
        # 'aniversarioperu',
        'indeciperu',
        # 'ernestocabralm',
    ]
    for twitter_user in users:
        # send mention
        for obj in lista:
            # status = "@" + twitter_user + " TEST " + message
            # status = message
            status = obj['tuit'] + " cc @" + twitter_user
            # status = message

            # should we tuit this message?
            to_tuit = lib.insert_to_db(status)
            if to_tuit == "do_tuit":

                # print status
                payload = {'status': status}
                url = "https://api.twitter.com/1.1/statuses/update.json"

                try:
                    print("Tweet ", payload)
                    if debug == 0:
                        r = requests.post(url=url, auth=oauth, params=payload)
                        # print json.loads(r.text)['id_str']
                        save_tuit(status)
                except:
                    print("Error")
