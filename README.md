# screepsapi

This is an unofficial client for the [Screeps](https://screeps.com/) Unoffical API.

Since the API is unofficial it could in theory change at any time. In practice though breaking changes are rare.

## Setup

Simply install the Python `screepsapi` library using `pip`.

## Usage

### Authentication

The recommended way to authenticate to the official servers is providing your [Authorization Token](https://docs.screeps.com/auth-tokens.html) into the `token` parameter.

```python
import screepsapi
TOKEN = "3bdd1da7-3002-4aaa-be91-330562f54093"
api = screepsapi.API(token=TOKEN)
```

An optional `prefix` parameter can be included with values such as `"/ptr"` for the Public Test Realm or `"/season"` for Seasonal Server.

It is also possible to access private servers with the `host` and `secure` parameters.

```python
import screepsapi
USER = "MyUsername"
PASSWORD = "TimeTravelingSecretAgentForHire"
HOST = "server1.screepspl.us:443"
api = screepsapi.API(USER, PASSWORD, host=HOST, secure=True)
```

Note that by default private servers do not use SSL and all traffic is unencrypted.

### API

The API class is a simple REST-based API. Each method corresponds to a different Screeps API endpoint.

The best way to discover functionality is to read through the [screepsapi library](screepsapi/screepsapi.py) or [Endpoints.md](docs/Endpoints.md)

#### Console Example

```python
import screepsapi
TOKEN = "3bdd1da7-3002-4aaa-be91-330562f54093"
api = screepsapi.API(token=TOKEN)

# Run "Game.time" on shard1 via the console
api.console("Game.time", shard="shard1")
```

#### User Information Example

```python
import screepsapi
TOKEN = "3bdd1da7-3002-4aaa-be91-330562f54093"
api = screepsapi.API(token=TOKEN)

# Find the GCL for "tedivm"
user = api.user_find("tedivm")
print user["user"]["gcl"]
```

### Socket

Screeps provides a sizable amount of data over a websocket. This includes console data and room details.

The best way to utilize the socket is to extend `screepsapi.Socket` and override the various abstract functions.

## Credentials

App developers are encouraged to align with [SS3: Unified Credentials File v1.0](https://github.com/screepers/screepers-standards/blob/master/SS3-Unified_Credentials_File.md) to standardize Screeps credentials storage with other third party tools.
