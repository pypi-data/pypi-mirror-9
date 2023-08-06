import json
import re
import requests
from urllib import quote, quote_plus

from blackbelt.config import config
from blackbelt.errors import ConfigurationError

class Github(object):
    """
    I represent a authenticated connection to Github API.
    Dispatch all requests to it through my methods.

    My actions are named from the BlackBelt's POW; I don't aim to be a full,
    usable client.
    """

    API_KEY = ""  # probably coming soon, trello-style
    APP_NAME = 'black-belt'
    URL_PREFIX = "https://api.github.com"

    def __init__(self, access_token=None):
        self._access_token = access_token
        if not self._access_token and config.get('github') and config['github'].get('access_token'):
            self._access_token = config['github']['access_token']
