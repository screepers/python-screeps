# Copyright @dzhu, @tedivm, @admon84
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

# Constants
OFFICIAL_HOST = 'screeps.com'
PTR_PREFIX = '/ptr'
DEFAULT_SHARD = 'shard0'
OFFICIAL_HISTORY_INTERVAL = 100
PRIVATE_HISTORY_INTERVAL = 20

class API(object):
    
    def req(self, func, path, **args):
        r = func(self.url + path, headers={'X-Token': self.token, 'X-Username': self.token}, **args)
        r.raise_for_status()
        if 'X-Token' in r.headers and len(r.headers['X-Token']) >= 40:
            self.token = r.headers['X-Token']
        try:
            return json.loads(r.text, object_pairs_hook=OrderedDict)
        except ValueError:
            print('JSON failure:', r.text)
        return None

    def get(self, _path, **args): return self.req(requests.get, _path, params=args)
    def post(self, _path, **args): return self.req(requests.post, _path, json=args)

    def __init__(self, u=None, p=None, token=None, host=None, prefix=None, secure=True, ptr=False):
        prefix = PTR_PREFIX if ptr else prefix
        
        self.host = host
        self.prefix = prefix
        self.secure = secure

        self.url = 'https://' if secure else 'http://'
        self.url += host if host else OFFICIAL_HOST
        self.url += prefix if prefix else ''
        self.url += '/api/'

        self.token = None
        if u is not None and p is not None:
            signin = self.signin(email=u, password=p)
            self.token = signin['token']
        elif token is not None:
            self.token = token


    #### auth methods

    def me(self):
        return self.get('auth/me')
    
    def signin(self, email=None, password=None):
        return self.post('auth/signin', email=email, password=password)
    
    def steam_ticket(self, ticket, useNativeAuth=False):
        return self.post('auth/steam-ticket', ticket=ticket, useNativeAuth=useNativeAuth)

    def query_token(self, token=None):
        return self.get('auth/query-token', token=token)

    
    #### register methods

    def check_email(self, email):
        return self.get('register/check-email', email=email)

    def check_username(self, username):
        return self.get('register/check-username', username=username)

    def set_username(self, username):
        return self.post('register/set-username', username=username)

    def register(self, username, email, password, modules):
        return self.post('register/submit', username=username, email=email, password=password, modules=modules)

    
    #### messaging methods

    def msg_index(self):
        return self.get('user/messages/index')

    def msg_list(self, respondent):
        return self.get('user/messages/list', respondent=respondent)

    def msg_unread(self):
        return self.get('user/messages/unread-count')

    def msg_send(self, respondent, text):
        return self.post('user/messages/send', respondent=respondent, text=text)

    def msg_mark_read(self, msg_id):
        return self.post('user/messages/mark-read', id=msg_id)


    #### user methods

    def overview(self, interval=8, statName='energyHarvested'):
        return self.get('user/overview', interval=interval, statName=statName)

    def stats(self, user_id, interval=8):
        return self.get('user/stats', id=user_id, interval=interval)

    def user_find(self, username=None, user_id=None):
        if username is not None:
            return self.get('user/find', username=username)
        if user_id is not None:
            return self.get('user/find', id=user_id)
        return False

    def user_rooms(self, user_id, shard=DEFAULT_SHARD):
        return self.get('user/rooms', id=user_id, shard=shard)

    def set_user_email(self, email):
        return self.post('user/email', email=email)

    def user_name(self):
        return self.get('user/name')

    def user_notify_prefs(self, prefs):
        return self.post('user/notify-prefs', prefs)
    
    def tutorial_done(self):
        return self.post('user/tutorial-done')

    def memory(self, path='', shard=DEFAULT_SHARD):
        ret = self.get('user/memory', path=path, shard=shard)
        if 'data' in ret:
            try:
                gzip_input = StringIO(b64decode(ret['data'][3:]))
            except:
                gzip_input = BytesIO(b64decode(ret['data'][3:]))
            gzip_string = GzipFile(fileobj=gzip_input).read().decode("utf-8")
            ret['data'] = json.loads(gzip_string)
        return ret

    def set_memory(self, path, value, shard=DEFAULT_SHARD):
        return self.post('user/memory', path=path, value=value, shard=shard)

    def get_segment(self, segment, shard=DEFAULT_SHARD):
        ret = self.get('user/memory-segment', segment=segment, shard=shard)
        if 'data' in ret and ret['data'][:3] == 'gz:':
            try:
                gzip_input = StringIO(b64decode(ret['data'][3:]))
            except:
                gzip_input = BytesIO(b64decode(ret['data'][3:]))
            gzip_string = GzipFile(fileobj=gzip_input).read().decode("utf-8")
            ret['data'] = json.loads(gzip_string)
        return ret

    def set_segment(self, segment, data, shard=DEFAULT_SHARD):
        return self.post('user/memory-segment', segment=segment, data=data, shard=shard)

    def console(self, cmd, shard=DEFAULT_SHARD):
        return self.post('user/console', expression=cmd, shard=shard)

    def get_code(self, branch):
        return self.get('user/code', branch=branch)

    def set_code(self, branch, modules, _hash=None):
        if _hash is None:
            _hash = int(time.time())
        return self.post('user/code', branch=branch, modules=modules, _hash=_hash)

    def branches(self):
        return self.get('user/branches')

    def set_active_branch(self, branch, activeName):
        return self.post('user/set-active-branch', branch=branch, activeName=activeName)

    def clone_branch(self, branch, newName, defaultModules):
        return self.post('user/clone-branch', branch=branch, newName=newName, defaultModules=defaultModules)

    def delete_branch(self, branch):
        return self.post('user/delete-branch', branch=branch)


    #### room info methods

    def room_overview(self, room, interval=8, shard=DEFAULT_SHARD):
        return self.get('game/room-overview', interval=interval, room=room, shard=shard)

    def room_terrain(self, room, encoded=False, shard=DEFAULT_SHARD):
        if encoded:
            return self.get('game/room-terrain', room=room, shard=shard, encoded=('1' if encoded else None))
        else:
            return self.get('game/room-terrain', room=room, shard=shard)

    def room_status(self, room, shard=DEFAULT_SHARD):
        return self.get('game/room-status', room=room, shard=shard)

    def room_objects(self, room, shard=DEFAULT_SHARD):
        return self.get('game/room-objects', room=room, shard=shard)

    def room_decorations(self, room, shard=DEFAULT_SHARD):
        return self.get('game/room-decorations', room=room, shard=shard)


    #### market info methods

    def orders_index(self, shard=DEFAULT_SHARD):
        return self.get('game/market/orders-index', shard=shard)

    def my_orders(self, shard=DEFAULT_SHARD):
        return self.get('game/market/my-orders', shard=shard)

    def market_order_by_type(self, resourceType, shard=DEFAULT_SHARD):
        return self.get('game/market/orders', resourceType=resourceType, shard=shard)

    def market_history(self, page=0):
        return self.get('user/money-history', page=page)


    #### leaderboard methods

    ## omit season to get current season
    def board_list(self, limit=10, offset=0, season=None, mode='world'):
        if season is None:
            ## find current season (the one with max start time among all seasons)
            seasons = self.board_seasons()['seasons']
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


    #### world manipulation methods

    def gen_unique_name(self, type):
        return self.post('game/gen-unique-object-name', type=type)
    
    def check_unique_name(self, type, name=None, shard=DEFAULT_SHARD):
        return self.post('game/check-unique-object-name', type=type, name=name, shard=shard)

    def gen_unique_flag(self, shard=DEFAULT_SHARD):
        return self.post('game/gen-unique-flag-name', shard=shard)
    
    def check_unique_flag(self, name=None, shard=DEFAULT_SHARD):
        return self.post('game/check-unique-flag-name', name=name, shard=shard)

    def flag_create(self, room, x, y, name=None, color='white', secondaryColor=None, shard=DEFAULT_SHARD):
        if name is None:
            name = self.gen_unique_name('flag')['name']
        if secondaryColor is None:
            secondaryColor = color

        return self.post('game/create-flag', room=room, x=x, y=y, name=name, color=color, secondaryColor=secondaryColor, shard=DEFAULT_SHARD)

    def flag_change_pos(self, _id, room, x, y):
        return self.post('game/change-flag', _id=_id, room=room, x=x, y=y)

    def flag_remove(self, name, room, shard=DEFAULT_SHARD):
        return self.post('game/remove-flag', name=name, room=room, shard=shard)

    def flag_change_color(self, _id, color, secondaryColor=None, shard=DEFAULT_SHARD):
        if secondaryColor is None:
            secondaryColor = color

        return self.post('game/change-flag-color', _id=_id, color=color, secondaryColor=secondaryColor, shard=DEFAULT_SHARD)

    def create_site(self, type, room, x, y, shard=DEFAULT_SHARD):
        return self.post('game/create-construction', structureType=type, room=room, x=x, y=y, shard=shard)

    def place_spawn(self, room, name, x, y, shard=DEFAULT_SHARD):
        return self.post('game/place-spawn', room=room, name=name, x=x, y=y, shard=shard)

    def badge(self, badge):
        return self.post('user/badge', badge=badge)

    def respawn(self):
        return self.post('user/respawn')

    def respawn_prohibited_rooms(self, shard=DEFAULT_SHARD):
        return self.get('user/respawn-prohibited-rooms', shard=shard)

    def add_object_intent(self, room, name, intent, shard=DEFAULT_SHARD):
        return self.post('game/add-object-intent', room=room, name=name, intent=intent, shard=shard)

    def set_notify_attacked(self, _id, enabled=True, shard=DEFAULT_SHARD):
        return self.post('game/set-notify-when-attacked', _id=_id, enabled=enabled, shard=shard)

    def create_invader(self, x, y, size, type, boosted=False, shard=DEFAULT_SHARD):
        return self.post('game/create-invader', x=x, y=y, size=size, type=type, boosted=boosted, shard=shard)

    def remove_invader(self, _id, shard=DEFAULT_SHARD):
        return self.post('game/remove-invader', _id=_id, shard=shard)


    #### battle info methods

    def battles(self, interval=100):
        return self.get('experimental/pvp', interval=interval)

    def nukes(self):
        return self.get('experimental/nukes')

    
    #### season methods

    def scoreboard(self, limit=20, offset=0):
        return self.get('scoreboard/list', limit=limit, offset=offset)


    #### decoration methods

    def inventory(self):
        return self.get('decorations/inventory')

    def themes(self):
        return self.get('decorations/themes')

    ## decorations is a string array of ids
    def convert(self, decorations):
        return self.post('decorations/convert', decorations=decorations)

    def pixelize(self, count, theme=''):
        return self.post('decorations/pixelize', count=count, theme=theme)

    def activate(self, _id, active):
        return self.post('decorations/activate', _id=_id, active=active)

    ## decorations is a string array of ids
    def deactivate(self, decorations):
        return self.post('decorations/deactivate', decorations=decorations)


    #### other methods

    def servers_list(self):
        return self.post('servers/list')
    
    def version(self):
        return self.get('version')

    def time(self, shard=DEFAULT_SHARD):
        return self.get('game/time', shard=shard)['time']

    def map_stats(self, rooms, statName, shard=DEFAULT_SHARD):
        return self.post('game/map-stats', rooms=rooms, statName=statName, shard=shard)

    def worldsize(self, shard=DEFAULT_SHARD):
        return self.get('game/world-size', shard=shard)

    def world_status(self):
        return self.get('user/world-status')

    def world_start_room(self, shard=None):
        return self.get('user/world-start-room', shard=shard)

    def history(self, room, tick, shard=DEFAULT_SHARD):
        if self.host == OFFICIAL_HOST:
            tick -= (tick % OFFICIAL_HISTORY_INTERVAL)
            return self.get('../room-history/%s/%s/%s.json' % (shard, room, tick))
        else:
            tick -= (tick % PRIVATE_HISTORY_INTERVAL)
            return self.get('../room-history', room=room, time=tick)

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
        if self.prefix == PTR_PREFIX:
            return self.post('user/activate-ptr')


class Socket(object):

    def __init__(self, user=None, password=None, logging=False, host=None, prefix=None, secure=True, token=None, ptr=False):
        prefix = PTR_PREFIX if ptr else prefix
        self.settings = {}
        self.user = user
        self.password = password
        self.host = host
        self.prefix = prefix
        self.secure = secure
        self.logging = False
        self.token = None
        self.user_id = None
        self.atoken = token

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws):
        self.disconnect()

    def on_open(self, ws):
        assert self.token != None
        ws.send('gzip on')
        ws.send('auth ' + self.token)
        self.token = None

    def gzip(self, enable):
        if enable:
            self.ws.send('gzip on')
        else:
            self.ws.send('gzip off')

    def subscribe_user(self, watchpoint):
        self.subscribe('user:' + self.user_id + '/' + watchpoint)

    def subscribe(self, watchpoint):
        self.ws.send('subscribe ' + watchpoint)

    def set_subscriptions(self):
        pass

    def process_log(self, ws, message, shard=DEFAULT_SHARD):
        pass

    def process_results(self, ws, message, shard=DEFAULT_SHARD):
        pass

    def process_error(self, ws, message, shard=DEFAULT_SHARD):
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
                    shard = DEFAULT_SHARD

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
        screepsConnection = API(
            u=self.user,
            p=self.password,
            host=self.host,
            prefix=self.prefix,
            secure=self.secure,
            token=self.atoken)
        me = screepsConnection.me()
        self.user_id = me['_id']
        self.token = screepsConnection.token

        if self.logging:
            logging.getLogger('websocket').addHandler(logging.StreamHandler())
            websocket.enableTrace(True)
        else:
            logging.getLogger('websocket').addHandler(logging.NullHandler())
            websocket.enableTrace(False)

        prefix = PTR_PREFIX if ptr else prefix

        url = 'wss://' if self.secure else 'ws://'
        url += self.host if self.host else OFFICIAL_HOST
        url += self.prefix if self.prefix else ''
        url += '/socket/websocket'

        self.ws = websocket.WebSocketApp(
            url=url,
            on_message=lambda ws, message: self.on_message(ws,message),
            on_error=lambda ws, error: self.on_error(ws,error),
            on_close=lambda ws: self.on_close(ws),
            on_open=lambda ws: self.on_open(ws))

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
