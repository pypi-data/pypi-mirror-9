# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import requests
from requests_oauthlib import OAuth1

from salvitobot import config
from salvitobot.exceptions import NoTwitterToken


REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
AUTHORIZE_URL = "https://api.twitter.com/oauth/authorize?oauth_token="
ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"


CONSUMER_KEY = config.key
CONSUMER_SECRET = config.secret


OAUTH_TOKEN = config.token
OAUTH_TOKEN_SECRET = config.token_secret


def get_oauth():
    oauth = OAuth1(
        CONSUMER_KEY,
        client_secret=CONSUMER_SECRET,
        resource_owner_key=OAUTH_TOKEN,
        resource_owner_secret=OAUTH_TOKEN_SECRET,
    )
    return oauth


def post_to_twitter(quakes_to_write):
    if not OAUTH_TOKEN:
        raise NoTwitterToken("You need to create and ``app`` en Twitter and add your keys to config.json")
    else:
        oauth = get_oauth()

    for obj in quakes_to_write:
        status = obj['tuit']

        payload = {'status': status}
        url = "https://api.twitter.com/1.1/statuses/update.json"

        try:
            requests.post(url=url, auth=oauth, params=payload)
        except:
            print("Error")
