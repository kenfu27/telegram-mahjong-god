import ConfigParser
import time
import random

import requests
from tornado import gen

from web import MJGWebModule, MJGRequestHandler

config = ConfigParser.RawConfigParser()
config.read("config.conf")
METABASE_HOST = config.get('Metabase', 'HOST')


class StatsWebModule(MJGWebModule):
    METABASE_TOKEN = None

    def __init__(self):
        super(StatsWebModule, self).__init__()


def get_metabase_token():
    def refresh_token():
        r = requests.post(METABASE_HOST + '/api/session',
                          json={
                              'email': config.get('Metabase', 'EMAIL'),
                              'password': config.get('Metabase', 'PASSWORD')
                          })

        StatsWebModule.METABASE_TOKEN = r.json()['id']

    if not StatsWebModule.METABASE_TOKEN:
        refresh_token()
    else:
        r = requests.get(METABASE_HOST + '/api/activity',
                         headers={'X-Metabase-Session': StatsWebModule.METABASE_TOKEN})

        if r.status_code == 401:
            refresh_token()

    return StatsWebModule.METABASE_TOKEN


@StatsWebModule.register_handler(r"/test")
class GeneralStatsHandler(MJGRequestHandler):
    @gen.coroutine
    def get(self):
        r = requests.post(METABASE_HOST + '/api/card/2/query', {'X-Metabase-Session': get_metabase_token()})

        self.set_header('Content-Type', 'application/json; charset="utf-8"')

        self.write({
            'time': time.time() + random.randint(0, 1000),
            'online': random.randint(0, 1)
        })
