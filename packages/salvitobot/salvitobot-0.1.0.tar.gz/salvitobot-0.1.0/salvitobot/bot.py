from datetime import datetime
from datetime import timedelta as td
import re

import feedparser


def get_tsunami_feed():
    warning = False
    watch = False
    out = False

    tsunamis = []

    url = "http://ptwc.weather.gov/feeds/ptwc_rss_pacific.xml"
    # url = r"rss.txt"
    d = feedparser.parse(url)
    for i in d.entries:
        description = i.description.replace("\n", " ")
        description = re.sub("\s+", " ", description)
        pubdate = datetime.strptime(i.published, '%d %b %Y %H:%M:%S %Z')
        pubdate -= td(hours=5)
        pubdate = pubdate.strftime('%H:%M') + " del " + pubdate.strftime('%d %b')

        pattern = "(A TSUNAMI WARNING IS IN EFFECT FOR(\s+\w+\s*\/*)+)"
        match = re.search(pattern, description, re.M)
        if match:
            if 'PERU' in match.groups()[0]:
                warning = True

        pattern = "(A TSUNAMI WATCH IS IN EFFECT FOR(\s+\w+\s*\/*)+)"
        match = re.search(pattern, description, re.M)
        if match:
            if 'PERU' in match.groups()[0]:
                watch = True

        if warning or watch:
            out = i.category.upper()
            if warning:
                out += ". Alerta de tsunami para PERU "
            if watch:
                out += ". Precaución de tsunami para PERU "
            out += "reportado a las " + str(pubdate) + " "
            out += i.link
            obj['tuit'] = out
            tsunamis.append(obj)
    return tsunamis


def save_tuit(message):
    lib.create_database()
    lib.insert_to_db(message)


def main():
    debug = 0

    # time_difference between the server time and Lima
    time_difference = 1

    print("Buscando tsunamis")
    tsunamis = get_tsunami_feed()
    # print json.dumps(tsunamis, indent=4)

    print("Buscando sismos")
    sismos = extractor.get_items()
    # print json.dumps(sismos, indent=4)

    if len(sismos) > 0:
        tuit(sismos, debug)
    if len(tsunamis) > 0:
        tuit(tsunamis, debug)


if __name__ == "__main__":
    main()
