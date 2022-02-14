Start by sending a request to `auth/signin` with your e-mail address and
password in a JSON object in the POST data. The response JSON object contains a
token (a hex string); remember that value. Each time you make a request that
requires authentication (the leaderboard and terrain ones, at least, don't),
send the most recent token value as both the `X-Token` and `X-Username`
headers. The response will contain a new token value in the `X-Token` header
with which you should replace your saved token. (You can send the token on every
request and just check for a new one in the response, so you don't have to know
exactly which calls require authentication.)

Example request parameters are given below, along with schemata for the server's
responses.

Memory and console endpoints are from
[bzy-xyz](https://gist.github.com/bzy-xyz/9c4d8c9f9498a2d7983d).

You can access the PTR by changing `screeps.com` to `screeps.com/ptr` in all URLs.

# Enumeration values

When an endpoint takes `interval` or `statName` as an argument, the valid values
are the ones listed below.

- interval: 8, 180, 1440 (8 for 1h, 180 for 24h and 1440 for 7 days)
- statName: creepsLost, creepsProduced, energyConstruction, energyControl, energyCreeps, energyHarvested

# Authentication

- [POST] `https://screeps.com/api/auth/signin`
    - post data: `{ email, password }`
    - response: `{ ok, token }`

- [POST] `https://screeps.com/api/auth/steam-ticket`
    - post data: `{ ticket, useNativeAuth }`

- [POST] `https://screeps.com/api/auth/query-token`
    - post data: `{ token }`

# Registration

- [GET] `https://screeps.com/api/register/check-email?email=user@example.com`

- [GET] `https://screeps.com/api/register/check-username?username=danny`

- [POST] `https://screeps.com/api/register/set-username`
    - post data: `{ username }`

- [POST] `https://screeps.com/api/register/submit`
    - post data: `{ username, email, password, modules }`

# Messaging

- [GET] `https://screeps.com/api/user/messages/index`
    - `{ ok, messages: [ { _id, message: { _id, user, respondent, date, type, text, unread } } ], users: { <user's _id>: { _id, username, badge: { type, color1, color2, color3, param, flip } } } }`

- [GET] `https://screeps.com/api/user/messages/list?respondent={userId}`
    - `{ ok, messages: [ { _id, date, type, text, unread } ] }`

- [GET] `https://screeps.com/api/user/messages/unread-count`
    - `{ ok, count }`

- [POST] `https://screeps.com/api/user/messages/send`
    - post data: `{ respondent, text }`
    - response: `{ ok }`

- [POST] `https://screeps.com/api/user/messages/mark-read`
    - post data: `{ id }`

# Room information

- [GET] `https://screeps.com/api/game/room-overview?interval=8&room=E1N8`
    - `{ ok, owner: { username, badge: { type, color1, color2, color3, param, flip } }, stats: { energyHarvested: [ { value, endTime } ], energyConstruction: [ { value, endTime } ], energyCreeps: [ { value, endTime } ], energyControl: [ { value, endTime } ], creepsProduced: [ { value, endTime } ], creepsLost: [ { value, endTime } ] }, statsMax: { energy1440, energyCreeps1440, energy8, energyControl8, creepsLost180, energyHarvested8, energy180, energyConstruction180, creepsProduced8, energyControl1440, energyCreeps8, energyHarvested1440, creepsLost1440, energyConstruction1440, energyHarvested180, creepsProduced180, creepsProduced1440, energyCreeps180, energyControl180, energyConstruction8, creepsLost8 } }`

- [GET] `https://screeps.com/api/game/room-terrain?room=E1N8`
    - `{ ok, terrain: [ { room, x, y, type } ] }`
    - `type` in each element of `terrain` can be "wall" or "swamp"

- [GET] `https://screeps.com/api/game/room-terrain?room=E1N8&encoded=1`
    - `{ ok, terrain: [ { _id, room, terrain, type } ] }`
    - `terrain` is a string of digits, giving the terrain left-to-right and top-to-bottom
    - 0: plain, 1: wall, 2: swamp, 3: also wall
    - encoded argument can be anything non-empty

- [GET] `https://screeps.com/api/game/room-status?room=E1N8`
    - `{ _id, status, novice }`
    - `status` can at least be "normal" or "out of borders"
    - if the room is in a novice area, `novice` will contain the Unix timestamp of the end of the protection (otherwise it is absent)

- [GET] `https://screeps.com/api/game/room-objects?room=E1N8`
    - `{ ok, objects: [ { _id, room, type, x, y } ], users: { <user's _id>: { _id, username, badge: { type, color1, color2, color3, param, flip } } } }`
    - `objects` contains a list of all game objects in the room (creeps, structures, sources, mineral, etc)

- [GET] `https://screeps.com/api/experimental/pvp?interval=100`
    - `{ ok, time, rooms: [ { _id, lastPvpTime } ] }`
    - `time` is the current server tick
    - `_id` contains the room name for each room, and `lastPvpTime` contains the last tick pvp occurred
    - if neither a valid `interval` nor a valid `start` argument is provided, the result of the call is still `ok`, but with an empty rooms array.

- [GET] `https://screeps.com/api/experimental/nukes`
    - `{ ok, nukes, <shard name>: [ { _id, type, room, x, y, landTime, launchRoomName } ] }`

# Market information

- [GET] `https://screeps.com/api/game/market/orders-index`
    - `{"ok":1,"list":[{"_id":"XUHO2","count":2}]}`
    - `_id` is the resource type, and there will only be one of each type.
    - `count` is the number of orders.

- [GET] `https://screeps.com/api/game/market/my-orders`
    - `{ ok, list: [ { _id, created, user, active, type, amount, remainingAmount, resourceType, price, totalAmount, roomName } ] }`

- [GET] `https://screeps.com/api/game/market/orders?resourceType=Z`
    - `{ ok, list: [ { _id, created, user, active, type, amount, remainingAmount, resourceType, price, totalAmount, roomName } ] }`
    - `resourceType` is one of the RESOURCE_* constants.

- [GET] `https://screeps.com/api/user/money-history`
    - `{"ok":1,"page":0,"list":[ { _id, date, tick, user, type, balance, change, market: {} } ] }`
    - `page` used for pagination.
    - `hasMore` is true if there are more pages to view.
    - `market`
      - New Order- `{ order: { type, resourceType, price, totalAmount, roomName } }`
      - Extended Order- `{ extendOrder: { orderId, addAmount } }`
      - Fulfilled Order- `{ resourceType, roomName, targetRoomName, price, npc, amount }`
      - Price Change - `{ changeOrderPrice: { orderId, oldPrice, newPrice } }`

# Leaderboard

- [GET] `https://screeps.com/api/leaderboard/seasons`
    - `{ ok, seasons: [ { _id, name, date } ] }`
    - the `_id` returned here is used for the season name in the other leaderboard calls

- [GET] `https://screeps.com/api/leaderboard/find?mode=world&season=2015-09&username=danny`
    - `{ ok, _id, season, user, score, rank }`
    - `user` (not `_id`) is the user's _id, as returned by `me` and `user/find`
    - `rank` is 0-based

- [GET] `https://screeps.com/api/leaderboard/find?mode=world&username=danny`
    - `{ ok, list: [ _id, season, user, score, rank ] }`
    - lists ranks in all seasons

- [GET] `https://screeps.com/api/leaderboard/list?limit=10&mode=world&offset=10&season=2015-09`
    - `{ ok, list: [ { _id, season, user, score, rank } ], count, users: { <user's _id>: { _id, username, badge: { type, color1, color2, color3, param, flip }, gcl } } }`

# Messages

- [GET] `https://screeps.com/api/user/messages/index`
    - `{ ok, messages: [ { _id, message: { _id, user, respondent, date, type, text, unread } } ], users: { <user's _id>: { _id, username, badge: { type, color1, color2, color3, param, flip } } } }`

- [GET] `https://screeps.com/api/user/messages/list?respondent=55605a6654db1fa952de8d90`
    - `{ ok, messages: [ { _id, date, type, text, unread } ] }`

- [POST] `https://screeps.com/api/user/messages/send`
    - post data: `{ respondent, text }`
    - `respondent` is the long _id of the user, not the username
    - response: `{ ok }`

- [GET] `https://screeps.com/api/user/messages/unread-count`
    - `{ ok, count }`

# User information and settings

- [GET] `https://screeps.com/api/auth/me`
    - `{ ok, _id, email, username, cpu, badge: { type, color1, color2, color3, param, flip }, password, notifyPrefs: { sendOnline, errorsInterval, disabledOnMessages, disabled, interval }, gcl, credits, lastChargeTime, lastTweetTime, github: { id, username }, twitter: { username, followers_count } }`

- [GET] `https://screeps.com/api/user/name`

- [GET] `https://screeps.com/api/user/stats?interval=8`

- [GET] `https://screeps.com/api/user/rooms?interval=8`

- [GET] `https://screeps.com/api/user/find?id={userId}`
    - `{ ok, user: { _id, username, badge: { type, color1, color2, color3, param, flip }, gcl } }`

- [GET] `https://screeps.com/api/user/find?username=danny`
    - `{ ok, user: { _id, username, badge: { type, color1, color2, color3, param, flip }, gcl } }`

- [GET] `https://screeps.com/api/user/overview?interval=1440&statName=energyControl`
    - `{ ok, rooms: [ <room name> ], stats: { <room name>: [ { value, endTime } ] }, statsMax }`

- [GET] `https://screeps.com/api/user/respawn-prohibited-rooms`
    - `{ ok, rooms: [ <room name> ] }`

- [GET] `https://screeps.com/api/user/world-size`
    - `{ ok, width, height }`

- [GET] `https://screeps.com/api/user/world-status`
    - `{ ok, status }`
    - `status` can be `"lost"`, `"empty"` or `"normal"`, lost is when you loose all your spawns, empty is when you have respawned and not placed your spawn yet.

- [GET] `https://screeps.com/api/user/world-start-room`
    - `{ ok, room:  [ <room name> ] }`
    - `room` is an array, but seems to always contain only one element

- [POST] `https://screeps.com/api/user/console`
    - post data: `{ expression }`
    - response: `{ ok, result: { ok, n }, ops: [ { user, expression, _id } ], insertedCount, insertedIds: [ <mongodb id> ] }`

- [GET] `https://screeps.com/api/user/memory?path=flags.Flag1`
    - `{ ok, data }`
    - `data` is the string `gz:` followed by base64-encoded gzipped JSON encoding of the requested memory path
    - the path may be empty or absent to retrieve all of Memory

- [POST] `https://screeps.com/api/user/memory`
    - post data: `{ path, value }`
    - response: `{ ok, result: { ok, n }, ops: [ { user, expression, hidden } ], data, insertedCount, insertedIds }`

- [GET] `https://screeps.com/api/user/memory-segment?segment=[0-99]`
    - `{ ok, data }`

- [POST] `https://screeps.com/api/user/memory-segment`
    - post data: `{ segment, data }`

- [GET/POST] `https://screeps.com/api/user/code`
    - for pushing or pulling code, as documented at http://support.screeps.com/hc/en-us/articles/203022612

- [GET] `https://screeps.com/api/user/branches`
    - `{ ok, list: [ { _id, branch, activeWorld, activeSim } ] }`

- [POST] `https://screeps.com/api/user/set-active-branch`
    - post data: `{ branch, activeName }`

- [POST] `https://screeps.com/api/user/clone-branch`
    - post data: `{ branch, newName, defaultModules }`

- [POST] `https://screeps.com/api/user/delete-branch`
    - post data: `{ branch }`

- [POST] `https://screeps.com/api/user/notify-prefs`
    - post data: `{ prefs }`
    - `prefs` can be any of: `disabled`, `disabledOnMessages`, `sendOnline`, `interval`, `errorsInterval`

- [POST] `https://screeps.com/api/user/tutorial-done`

- [POST] `https://screeps.com/api/user/badge?badge={Badge}`
    - `badge` object format: `{ type, color1, color2, color3, param, flip }`


# Manipulating the game world

- [POST] `https://screeps.com/api/game/gen-unique-object-name`
    - post data: `{ type }`
    - response: `{ ok, name }`
    - `type` can be at least "flag" or "spawn"

- [POST] `https://screeps.com/api/game/check-unique-object-name`
    - post data: `{ type, name, shard }`

- [POST] `https://screeps.com/api/game/gen-unique-flag-name`
    - post data: `{ shard }`

- [POST] `https://screeps.com/api/game/create-flag`
    - post data: `{ room, x, y, name, color, secondaryColor }`
    - response: `{ ok, result: { nModified, ok, upserted: [ { index, _id } ], n }, connection: { host, id, port } }`
    - if the name is new, `result.upserted[0]._id` is the game id of the created flag
    - if not, this moves the flag and the response does not contain the id (but the id doesn't change)
    - `connection` looks like some internal MongoDB thing that is irrelevant to us

- [POST] `https://screeps.com/api/game/change-flag`
    - post data: `{ _id, room, x, y }`
    - response: `{ ok, result: { nModified, ok, n }, connection: { host, id, port } }`

- [POST] `https://screeps.com/api/game/change-flag-color`
    - post data: `{ _id, color, secondaryColor }`
    - response: `{ ok, result: { nModified, ok, n }, connection: { host, id, port } }`

- [POST] `https://screeps.com/api/game/remove-flag`
    - post data: `{ room, name, shard }`

- [POST] `https://screeps.com/api/game/add-object-intent`
    - post data: `{ _id, room, name, intent }`
    - response: `{ ok, result: { nModified, ok, upserted: [ { index, _id } ], n }, connection: { host, id, port } }`
    - `_id` is the game id of the object to affect (except for destroying structures), `room` is the name of the room it's in
    - this method is used for a variety of actions, depending on the `name` and `intent` parameters
        - remove flag: `name = "remove"`, `intent = {}`
        - destroy structure: `_id = "room"`, `name = "destroyStructure"`, `intent = [ {id: <structure id>, roomName, <room name>, user: <user id>} ]`
            - can destroy multiple structures at once
        - suicide creep: `name = "suicide"`, `intent = {id: <creep id>}`
        - unclaim controller: `name = "unclaim"`, `intent = {id: <controller id>}`
             - intent can be an empty object for suicide and unclaim, but the web interface sends the id in it, as described
        - remove construction site: `name = "remove"`, `intent = {}`

- [POST] `https://screeps.com/api/game/set-notify-when-attacked`
    - post data: `{ _id, enabled }`
    - `enabled` is either `true` or `false` (literal values, not strings)
    - response: `{ ok, result: { ok, nModified, n }, connection: { id, host, port } }`

- [POST] `https://screeps.com/api/game/create-construction`
    - post data: `{ room, structureType, x, y}`
    - `structureType` is the same value as one of the in-game STRUCTURE_* constants ('road', 'spawn', etc.)
    - `{ ok, result: { ok, n }, ops: [ { type, room, x, y, structureType, user, progress, progressTotal, _id } ], insertedCount, insertedIds }`

- [POST] `https://screeps.com/api/game/place-spawn`
    - post data: `{ room, name, x, y, shard }`

- [POST] `https://screeps.com/api/game/create-invader`
    - post data: `{ x, y, size, type, boosted, shard }`

- [POST] `https://screeps.com/api/game/remove-invader`
    - post data: `{ _id, shard }`

# Decorations

- [GET] `https://screeps.com/api/decorations/inventory`

- [GET] `https://screeps.com/api/decorations/themes`

- [POST] `https://screeps.com/api/decorations/convert`
    - post data: `{ decorations }`
    - `decorations` is a string array of ids

- [POST] `https://screeps.com/api/decorations/pixelize`
    - post data: `{ count, theme }`

- [POST] `https://screeps.com/api/decorations/activate`
    - post data: `{ _id, active}`

- [POST] `https://screeps.com/api/decorations/deactivate`
    - post data: `{ decorations }`
    - `decorations` is a string array of ids

# Other

- [POST] `https://screeps.com/api/servers/list`
    - `{ ok, servers }`

- [GET] `https://screeps.com/api/game/shards/info`
    - `{ ok, shards: [ { name, lastTicks, cpuLimit, rooms, users, tick } ] }`

- [GET] `https://screeps.com/api/version`
    - `{ ok, package, protocol, serverData, users }`

- [GET] `https://screeps.com/api/game/time`
    - `{ ok, time }`

- [POST] `https://screeps.com/api/game/map-stats`
    - post data: `{ rooms: [ <room name> ], statName: "..."}`
    - statName can be "owner0", "claim0", or a stat (see the enumeration above) followed by an interval
    - if it is owner0 or claim0, there's no separate stat block in the response
    - response: `{ ok, stats: { <room name>: { status, novice, own: { user, level }, <stat>: [ { user, value } ] } }, users: { <user's _id>: { _id, username, badge: { type, color1, color2, color3, param, flip } } } }`
    - `status` and `novice` are as per the `room-status` call
    - `level` can be 0 to indicate a reserved room

- [GET] `https://screeps.com/room-history/shard0/E1N8/12340.json`
    - `{ timestamp, room, base, ticks: { <time>: <tick update object> } }`
    - the number in the URL is the tick to retrieve information for (from 5e5 ticks ago to about 50 ticks ago)
        - note that the web interface only shows up to 3e5 ticks ago
    - the tick must be a multiple of 20; the response includes information for the 20 ticks starting then
    - for the first tick in the result, the tick update object maps from object ids to full object descriptions
    - for later ticks, the update includes only changed attributes
    - timestamp is milliseconds since the Unix epoch

- [POST] `https://screeps.com/api/user/activate-ptr`
    - `{ ok, result: { ok, nModified, n }, connection: { id, host, port } }`
	- only works on the Public Test Realm

- [GET] `https://screeps.com/api/scoreboard/list?limit=20&offset=0`
    - only works on Seasonal servers