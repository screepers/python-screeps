
# Copyright @dzhu
# https://gist.github.com/dzhu/d6999d126d0182973b5c

from base64 import b64decode
from collections import OrderedDict
from cStringIO import StringIO
from gzip import GzipFile
import json
import logging
import requests
from StringIO import StringIO
import sys
import websocket


## Python before 2.7.10 or so has somewhat broken SSL support that throws a warning; suppress it
import warnings; warnings.filterwarnings('ignore', message='.*true sslcontext object.*')

class API(object):
    def req(self, func, path, **args):
        r = func(self.prefix + path, headers={'X-Token': self.token, 'X-Username': self.token}, **args)
        self.token = r.headers.get('X-Token', self.token)
        try:
            return json.loads(r.text, object_pairs_hook=OrderedDict)
        except ValueError:
            print 'JSON failure:', r.text
        return None

    def get(self, _path, **args): return self.req(requests.get, _path, params=args)
    def post(self, _path, **args): return self.req(requests.post, _path, json=args)

    def __init__(self, u=None, p=None, ptr=False):
        self.ptr = ptr
        self.prefix = 'https://screeps.com/ptr/api/' if ptr else 'https://screeps.com/api/'
        self.token = None
        if u is not None and p is not None:
            self.token = self.post('auth/signin', email=u, password=p)['token']


    #### miscellaneous user methods

    def me(self):
        return self.get('auth/me')

    def overview(self, interval=8, statName='energyHarvested'):
        return self.get('user/overview', interval=interval, statName=statName)

    def stats(self,id,interval=8):
        return self.get('user/stats',id=id,interval=interval)

    def user_find(self, username):
        return self.get('user/find', username=username)

    def memory(self, path=''):
        ret = self.get('user/memory', path=path)
        if 'data' in ret:
            ret['data'] = json.load(GzipFile(fileobj=StringIO(b64decode(ret['data'][3:]))))
        return ret

    def set_memory(self, path, value):
        return self.post('user/memory', path=path, value=value)

    def console(self, cmd):
        return self.post('user/console', expression=cmd)


    #### room info methods

    def room_overview(self, room, interval=8):
        return self.get('game/room-overview', interval=interval, room=room)

    def room_terrain(self, room, encoded=False):
        return self.get('game/room-terrain', room=room, encoded=('1' if encoded else None))

    def room_status(self, room):
        return self.get('game/room-status', room=room)


    #### leaderboard methods

    ## omit season to get current season
    def board_list(self, limit=10, offset=0, season=None, mode='world'):
        if season is None:
            ## find current season (the one with max start time among all seasons)
            seasons = self.board_seasons['seasons']
            season = max(seasons, key=lambda s: s['date'])['_id']

        ret = self.get('leaderboard/list', limit=limit, offset=offset, mode=mode, season=season)
        for d in ret['list']:
            d['username'] = ret['users'][d['user']]['username']
        return ret

    ## omit season to get all seasons
    def board_find(self, username, season=None, mode='world'):
        return self.get('leaderboard/find', mode=mode, season=season, username=username)

    def board_seasons(self):
        return self.get('leaderboard/seasons')


    #### messaging methods

    def msg_index(self):
        return self.get('user/messages/index')

    def msg_list(self, respondent):
        return self.get('user/messages/list', respondent=respondent)

    def msg_send(self, respondent, text):
        return self.post('user/messages/send', respondent=respondent, text=text)


    #### world manipulation methods

    def gen_unique_name(self, type):
        return self.post('game/gen-unique-object-name', type=type)

    def flag_create(self, room, x, y, name=None, color='white', secondaryColor=None):
        if name is None:
            name = self.gen_unique_name('flag')['name']
        if secondaryColor is None:
            secondaryColor = color

        return self.post('game/create-flag', room=room, x=x, y=y, name=name, color=color, secondaryColor=secondaryColor)

    def flag_change_pos(self, _id, room, x, y):
        return self.post('game/change-flag', _id=_id, room=room, x=x, y=y)

    def flag_change_color(self, _id, color, secondaryColor=None):
        if secondaryColor is None:
            secondaryColor = color

        return self.post('game/change-flag-color', _id=_id, color=color, secondaryColor=secondaryColor)

    def create_site(self, typ, room, x, y):
        return self.post('game/create-construction', structureType=typ, room=room, x=x, y=y)


    #### other methods

    def time(self):
        return self.get('game/time')['time']

    def map_stats(self, rooms, statName):
        return self.post('game/map-stats', rooms=rooms, statName=statName)

    def history(self, room, tick):
        return self.get('../room-history/%s/%s.json' % (room, tick - (tick % 20)))

    def activate_ptr(self):
        if self.ptr:
            return self.post('user/activate-ptr')


class Socket(object):

    def __init__(self, user, password, ptr=False, logging=False):
        self.settings = {}
        self.user = user
        self.password = password
        self.ptr = ptr
        self.logging = False

    def on_error(self, ws, error):
        print error

    def on_close(self, ws):
        self.disconnect()

    def on_open(self, ws):
        screepsConnection = API(u=self.user,p=self.password,ptr=self.ptr)
        me = screepsConnection.me()
        self.user_id = me['_id']
        ws.send('auth ' + screepsConnection.token)

    def gzip(enable):
        if enable:
            ws.send('gzip on')
        else:
            ws.send('gzip off')

    def subscribe_user(self, watchpoint):
        self.subscribe('user:' + self.user_id + '/' + watchpoint)

    def subscribe(self, watchpoint):
        self.ws.send('subscribe ' + watchpoint)

    def set_subscriptions(self):
        pass

    def process_log(self, ws, message):
        pass

    def process_results(self, ws, message):
        pass

    def process_error(self, ws, message):
        pass

    def process_cpu(self, ws, data):
        pass

    def process_rawdata(self, ws, data):
        pass


    def on_message(self, ws, message):
        if (message.startswith('auth ok')):
            self.set_subscriptions()
            return

        if (message.startswith('time')):
            return

        if (message.startswith('gz')):
            gzipFile = GzipFile(fileobj=StringIO(b64decode(message[3:])))
            message = gzipFile.read()

        try:
            self.process_message(ws, message)
            return
        except AttributeError:

            try:
                data = json.loads(message)
            except:
                return

            if data[0].endswith('console'):

                if 'messages' in data[1]:
                    stream = []

                    if 'log' in data[1]['messages']:
                        for line in data[1]['messages']['log']:
                            self.process_log(ws, line)

                    if 'results' in data[1]['messages']:
                        for line in data[1]['messages']['results']:
                            self.process_results(ws, line)

                if 'error' in data[1]:
                    self.process_error(data[1]['error'])


            if data[0].endswith('cpu'):
                self.process_cpu(ws, data[1])

            self.process_rawdata(ws, data)

    def connect(self):
        if self.logging:
            logging.getLogger('websocket').addHandler(logging.StreamHandler())
            websocket.enableTrace(True)
        else:
            logging.getLogger('websocket').addHandler(logging.NullHandler())
            websocket.enableTrace(False)

        if not self.ptr:
            url = 'wss://screeps.com/socket/websocket'
        else:
            url = 'wss://screeps.com/ptr/socket/websocket'

        self.ws = websocket.WebSocketApp(url=url,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close,
                                    on_open=self.on_open)

        if 'http_proxy' in self.settings and self.settings['http_proxy'] is not None:
            http_proxy_port = self.settings['http_proxy_port'] if 'http_proxy_port' in self.settings else 8080
            self.ws.run_forever(http_proxy_host=self.settings['http_proxy'], http_proxy_port=http_proxy_port, ping_interval=1)
        else:
            self.ws.run_forever(ping_interval=1)


    def disconnect(self):
        if self.ws:
            self.ws.close()
            self.ws = false


    def start(self):
        self.connect()
