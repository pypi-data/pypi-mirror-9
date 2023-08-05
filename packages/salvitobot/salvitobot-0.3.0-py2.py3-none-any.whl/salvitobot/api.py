import codecs
import json
import os
import time

import requests

from . import config
from . import utils
from . import email
from . import wordpress
from . import twitter
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
        self.post_urls = []
        self.urls = [
            "http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_hour.geojson",
            "http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson",
        ]
        self.stories = None

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

    def is_new_quake(self, test=None):
        """

        :return: ``True`` or ``False``
        """
        # Reset quakes to write
        self._quakes_to_write = []

        db = utils.create_database(test)
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

    def write_stories(self):
        """
        Write story for new quakes.

        :return: text of post

        """
        if self.quake is None:
            # get quake function has not been called
            raise ProcedureError("You need to call the function .get_quake(country='MyCountry') first")
        else:
            if len(self._quakes_to_write) < 1:
                print("Nothing to do.")
                return "Nothing to do."
            else:
                writer = Writer()
                stories = writer.write_stories(self._quakes_to_write)
                self.stories = stories

    def post_to_wp(self):
        for item in self.stories:
            url_from_post = wordpress.post_to_wp(item['title'], item['body'], item['local_time'])
            self.post_urls.append(url_from_post)
            print(url_from_post)

    def send_email_to(self, email_receivers):
        email.send(email_receivers, self.stories)

    def tweet(self):
        twitter.post_to_twitter(self._quakes_to_write)
