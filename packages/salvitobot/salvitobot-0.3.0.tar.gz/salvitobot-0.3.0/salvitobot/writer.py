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
                        "grados se produjo el _date_local_str_ por la _time_of_day_ a " \
                        "_epicenter_, reportó el Servicio Geológico de EE.UU. \n" \
                        "El _tremor_ se registró a las _time_ de la _time_of_day_, " \
                        "hora local, a una profundidad de " \
                        "_depth_ kilómetros.\n\n" \
                        "Según el USGS, el epicentro se ubicó _nearby_cities_.\n"
        self.positive_historial_template = "En los últimos _days_ días, se han registrado " \
                                           "_how_many_ temblores de magnitud 3.0 o mayores en esta zona."
        self.negative_historial_template = "En los últimos _days_ días, no se registraron temblores de" \
                                           "magnitud 3.0 o mayores en esta zona."
        self.template_footer = "La información proviene del Servicio de Notificación del Servicio Geológico " \
                               "estadounidense. Este texto " \
                               "fue elaborado por un algoritmo escrito por " \
                               "<a href='https://twitter.com/AniversarioPeru'>@AniversarioPeru</a>."

    def write_stories(self, items):
        """

        :param items: list of earthquake data (as dictionaries)
        """
        stories = []
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
            date_local = item['datetime_local']
            a = arrow.get(date_local)
            date_local_str = a.format('DD MMM, YYYY', locale='es_es')
            time = datetime.datetime.strftime(date_local, '%I:%M')

            hour_of_day = int(datetime.datetime.strftime(date_local, '%H'))
            if 6 <= hour_of_day < 12:
                time_of_day = 'mañana'
            elif 12 <= hour_of_day < 18:
                time_of_day = 'tarde'
            elif 18 <= hour_of_day < 24:
                time_of_day = 'noche'
            elif hour_of_day == 24:
                time_of_day = 'madrugada'
            elif hour_of_day < 6:
                time_of_day = 'madrugada'

            epicenter = item['place']

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
            text = re.sub('_time_of_day_', time_of_day, text)
            text = re.sub('_epicenter_', epicenter, text)
            text = re.sub('_time_', time, text)
            text = re.sub('_depth_', depth, text)

            title = tremor.capitalize() + ' de ' + magnitude_integer + ' se registró a ' + epicenter

            story = {
                'title': title,
                'body': text,
                'local_time': item['datetime_local']
            }
            save_to_db(item)
            stories.append(story)
        return stories
