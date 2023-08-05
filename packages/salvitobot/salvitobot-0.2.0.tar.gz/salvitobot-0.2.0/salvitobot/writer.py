import datetime
from datetime import timedelta as td
import re

import arrow

from .utils import save_to_db
from .utils import extract_nearby_cities
from .wordpress import post_to_wp
from .exceptions import ToPublishPostError


class Writer(object):
    """Writes blog posts and uploads to Wordpress.

    """
    def __init__(self):
        self.template = "Un _tremor_ de _magnitude_level_ magnitud de _magnitude_integer_ " \
                        "grados tuvo lugar el _date_local_str_ por la _time_of_day1_ a " \
                        "_epicenter_ según el Servicio Geológico de EE.UU. \n" \
                        "El _tremor_ se produjo a las _time_ de la _time_of_day2_, " \
                        "del Tiempo universal coordinado (UTC), a una profundidad de " \
                        "_depth_ kilómetros. \n\n " \
                        "Según el USGS, el epicentro se ubicó _nearby_cities_.\n"
        self.positive_historial_template = "En los últimos _days_ días, se han registrado " \
                                           "_how_many_ temblores de magnitud 3.0 o mayores en esta zona."
        self.negative_historial_template = "En los últimos _days_ días, no se registraron temblores de" \
                                           "magnitud 3.0 o mayores en esta zona."
        self.template_footer = "La información proviene del USGS Earthquake Notification Service. Este post " \
                               "fue elaborado por un algoritmo escrito por el autor."

    def write_post(self, items, publish=None):
        """

        :param items: list of earthquake data (as dictionaries)
        :param publish: required, True or False to send to Wordpress

        :raises ToPublishPostError: Error if user does not specify to publish this post or not. Use
                                    ``publish=True`` or ``publish=False``.

        """
        if publish is None and publish is not True and publish is not False:
            raise ToPublishPostError("You need to specify to publish or not this post: publish=False")

        for item in items:
            nearby_cities = extract_nearby_cities(item)

            if item['magnitude'] > 7.5:
                tremor = 'terremoto'
            else:
                tremor = 'temblor'

            if item['magnitude'] >= 7:
                magnitude_level = 'gran'
            elif 4 < item['magnitude'] < 7:
                magnitude_level = 'mediana'
            else:
                magnitude_level = 'escasa'

            magnitude_integer = str(item['magnitude'])
            date_local = item['datetime_utc'] + td(minutes=item['tz'])
            a = arrow.get(date_local)
            date_local_str = a.format('DD MMM, YYYY', locale='es_es')

            hour_of_day = int(datetime.datetime.strftime(date_local, '%H'))
            print(hour_of_day)
            if 6 <= hour_of_day < 12:
                time_of_day1 = 'mañana'
            elif 12 <= hour_of_day < 18:
                time_of_day1 = 'tarde'
            elif 18 <= hour_of_day < 24:
                time_of_day1 = 'noche'
            elif hour_of_day == 24:
                time_of_day1 = 'madrugada'
            elif hour_of_day < 6:
                time_of_day1 = 'madrugada'

            epicenter = item['place']

            time = datetime.datetime.strftime(item['datetime_utc'], '%H:%M')
            hour_of_day = int(datetime.datetime.strftime(item['datetime_utc'], '%H'))
            if 6 <= hour_of_day < 12:
                time_of_day2 = 'mañana'
            elif 12 <= hour_of_day < 18:
                time_of_day2 = 'tarde'
            elif 18 <= hour_of_day < 24:
                time_of_day2 = 'noche'
            elif hour_of_day == 24:
                time_of_day2 = 'madrugada'
            elif hour_of_day < 6:
                time_of_day2 = 'madrugada'

            depth = str(item['depth'])

            text = self.template + "\n"
            # text += self.negative_historial_template + "\n"
            # TODO get historial from our database
            text += self.template_footer

            text = re.sub('_nearby_cities_', nearby_cities, text)
            text = re.sub('_tremor_', tremor, text)
            text = re.sub('_magnitude_level_', magnitude_level, text)
            text = re.sub('_magnitude_integer_', magnitude_integer, text)
            text = re.sub('_date_local_str_', date_local_str, text)
            text = re.sub('_time_of_day1_', time_of_day1, text)
            text = re.sub('_time_of_day2_', time_of_day2, text)
            text = re.sub('_epicenter_', epicenter, text)
            text = re.sub('_time_', time, text)
            text = re.sub('_depth_', depth, text)

            title = 'Temblor grado ' + magnitude_integer + ' en ' + epicenter

            if publish is True:
                post_to_wp(title, text)
                save_to_db(item)
                print("Published post with title %s" % title)

            if publish is False:
                print(text)
