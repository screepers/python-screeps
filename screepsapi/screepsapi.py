# Copyright @dzhu, @tedivm
# https://github.com/screepers/python-screeps

from base64 import b64decode
from collections import OrderedDict
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

from io import BytesIO
from gzip import GzipFile
import json
import logging
import requests
import ssl
import sys
import websocket
import zlib


## Python before 2.7.10 or so has somewhat broken SSL support that throws a warning; suppress it
import warnings; warnings.filterwarnings('ignore', message='.*true sslcontext object.*')

class API(object):
    def req(self, func, path, **args):
        r = func(self.prefix + path, headers={'X-Token': self.token, 'X-Username': self.token}, **args)
        r.raise_for_status()
        if 'X-Token' in r.headers and len(r.headers['X-Token']) >= 40:
            self.token = r.headers['X-Token']
        try:
            return json.loads(r.text, object_pairs_hook=OrderedDict)
        except ValueError:
            print ('JSON failure:', r.text)
        return None

    def get(self, _path, **args): return self.req(requests.get, _path, params=args)
    def post(self, _path, **args): return self.req(requests.post, _path, json=args)

    def __init__(self, u=None, p=None, ptr=False, host=None, secure=False):
        self.ptr = ptr
        self.host = host
        self.secure = secure
        if host is not None:
            self.prefix = 'https://' if secure else 'http://'
            self.prefix += host + '/api/'
        else:
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

    def user_find(self, username=None, user_id=None, shard='shard0'):
        if username is not None:
            return self.get('user/find', username=username, shard=shard)
        if user_id is not None:
            return self.get('user/find', id=user_id, shard=shard)
        return False

    def user_rooms(self, userid, shard='shard0'):
        return self.get('user/rooms', id=userid, shard=shard)

    def memory(self, path='', shard='shard0'):
        ret = self.get('user/memory', path=path, shard=shard)
        if 'data' in ret:
            try:
                gzip_input = StringIO(b64decode(ret['data'][3:]))
            except:
                gzip_input = BytesIO(b64decode(ret['data'][3:]))
            ret['data'] = json.load(GzipFile(fileobj=gzip_input))
        return ret

    def set_memory(self, path, value, shard='shard0'):
        return self.post('user/memory', path=path, value=value, shard=shard)

    def get_segment(self, segment, shard='shard0'):
        ret = self.get('user/memory-segment', segment=segment, shard=shard)
        if 'data' in ret and ret['data'][:3] == 'gz:':
            try:
                gzip_input = StringIO(b64decode(ret['data'][3:]))
            except:
                gzip_input = BytesIO(b64decode(ret['data'][3:]))
            ret['data'] = GzipFile(fileobj=gzip_input)
        return ret


    def set_segment(self, segment, data, shard='shard0'):
        return self.post('user/memory-segment', segment=segment, data=data, shard=shard)


    def console(self, cmd, shard='shard0'):
        return self.post('user/console', expression=cmd, shard=shard)


    #### room info methods

    def room_overview(self, room, interval=8, shard='shard0'):
        return self.get('game/room-overview', interval=interval, room=room, shard=shard)

    def room_terrain(self, room, encoded=False, shard='shard0'):
        if encoded:
            return self.get('game/room-terrain', room=room, shard=shard, encoded=('1' if encoded else None))
        else:
            return self.get('game/room-terrain', room=room, shard=shard)

    def room_status(self, room, shard='shard0'):
        return self.get('game/room-status', room=room, shard=shard)


    #### market info methods

    def orders_index(self, shard='shard0'):
        return self.get('game/market/orders-index', shard=shard)

    def my_orders(self, shard='shard0'):
        return self.get('game/market/my-orders', shard=shard)

    def market_order_by_type(self, resourceType, shard='shard0'):
        return self.get('game/market/orders', resourceType=resourceType, shard=shard)

    def market_history(self, page=None, shard='shard0'):
        return self.get('user/money-history', page=page, shard=shard)


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

    def flag_create(self, room, x, y, name=None, color='white', secondaryColor=None, shard='shard0'):
        if name is None:
            name = self.gen_unique_name('flag')['name']
        if secondaryColor is None:
            secondaryColor = color

        return self.post('game/create-flag', room=room, x=x, y=y, name=name, color=color, secondaryColor=secondaryColor, shard='shard0')

    def flag_change_pos(self, _id, room, x, y):
        return self.post('game/change-flag', _id=_id, room=room, x=x, y=y)

    def flag_change_color(self, _id, color, secondaryColor=None, shard='shard0'):
        if secondaryColor is None:
            secondaryColor = color

        return self.post('game/change-flag-color', _id=_id, color=color, secondaryColor=secondaryColor, shard='shard0')

    def create_site(self, type, room, x, y, shard='shard0'):
        return self.post('game/create-construction', structureType=type, room=room, x=x, y=y, shard=shard)

    def place_spawn(self, room, name, x, y, shard='shard0'):
        self.post('game/place-spawn', room=room, name=name, x=x, y=y, shard=shard)
        pass


    #### battle info methods

    def battles(self, interval=None, start=None):
        if start is not None:
            return self.get('experimental/pvp', start=start)
        if interval is not None:
            return self.get('experimental/pvp', interval=interval)
        return False

    def nukes(self):
        return self.get('experimental/nukes')


    #### other methods

    def time(self, shard='shard0'):
        return self.get('game/time', shard=shard)['time']

    def map_stats(self, rooms, statName, shard='shard0'):
        return self.post('game/map-stats', rooms=rooms, statName=statName, shard=shard)

    def worldsize(self, shard='shard0'):
        return self.get('game/world-size', shard=shard)

    def world_status(self):
        return self.get('user/world-status')

    def world_start_room(self, shard=None):
        return self.get('user/world-start-room', shard=shard)

    def history(self, room, tick):
        return self.get('../room-history/%s/%s.json' % (room, tick - (tick % 20)))

    def get_shards(self):
        try:
            shard_data = self.shard_info()['shards']
            shards = [x['name'] for x in shard_data]
            if len(shards) > 0:
                return shards
        except:
            pass
        return False

    def shard_info(self):
        return self.get('game/shards/info')

    def activate_ptr(self):
        if self.ptr:
            return self.post('user/activate-ptr')


class Socket(object):

    def __init__(self, user, password, ptr=False, logging=False, host=None, secure=None):
        self.settings = {}
        self.user = user
        self.password = password
        self.ptr = ptr
        self.host = host
        self.secure = secure
        self.logging = False
        self.token = None
        self.user_id = None

    def on_error(self, ws, error):
        print (error)

    def on_close(self, ws):
        self.disconnect()

    def on_open(self, ws):
        assert self.token != None
        ws.send('gzip on')
        ws.send('auth ' + self.token)
        self.token = None

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

    def process_log(self, ws, message, shard='shard0'):
        pass

    def process_results(self, ws, message, shard='shard0'):
        pass

    def process_error(self, ws, message, shard='shard0'):
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
            message = zlib.decompress(b64decode(message[3:]), 0).decode('utf-8')

        try:
            self.process_message(ws, message)
            return
        except AttributeError:

            try:
                data = json.loads(message)
            except:
                return

            if data[0].endswith('console'):
                if 'shard' in data[1]:
                    shard = data[1]['shard']
                else:
                    shard = 'shard0'

                if 'messages' in data[1]:
                    stream = []

                    if 'log' in data[1]['messages']:
                        for line in data[1]['messages']['log']:
                            self.process_log(ws, line, shard)

                    if 'results' in data[1]['messages']:
                        for line in data[1]['messages']['results']:
                            self.process_results(ws, line, shard)

                if 'error' in data[1]:
                    self.process_error(ws, data[1]['error'], shard)

            if data[0].endswith('cpu'):
                self.process_cpu(ws, data[1])

            self.process_rawdata(ws, data)

    def connect(self):
        screepsConnection = API(u=self.user,p=self.password,ptr=self.ptr,host=self.host,secure=self.secure)
        me = screepsConnection.me()
        self.user_id = me['_id']
        self.token = screepsConnection.token

        if self.logging:
            logging.getLogger('websocket').addHandler(logging.StreamHandler())
            websocket.enableTrace(True)
        else:
            logging.getLogger('websocket').addHandler(logging.NullHandler())
            websocket.enableTrace(False)

        if self.host:
            url = 'wss://' if self.secure else 'ws://'
            url += self.host + '/socket/websocket'
        elif not self.ptr:
            url = 'wss://screeps.com/socket/websocket'
        else:
            url = 'wss://screeps.com/ptr/socket/websocket'

        self.ws = websocket.WebSocketApp(url=url,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close,
                                    on_open=self.on_open)

        ssl_defaults = ssl.get_default_verify_paths()
        sslopt_ca_certs = {'ca_certs': ssl_defaults.cafile}
        if 'http_proxy' in self.settings and self.settings['http_proxy'] is not None:
            http_proxy_port = self.settings['http_proxy_port'] if 'http_proxy_port' in self.settings else 8080
            self.ws.run_forever(http_proxy_host=self.settings['http_proxy'], http_proxy_port=http_proxy_port, ping_interval=1, sslopt=sslopt_ca_certs)
        else:
            self.ws.run_forever(ping_interval=1, sslopt=sslopt_ca_certs)


    def disconnect(self):
        if self.ws:
            self.ws.close()
            self.ws = False


    def start(self):
        self.connect()
