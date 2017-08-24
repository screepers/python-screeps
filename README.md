# screepsapi

This is an unofficial client for the [Screeps](https://screeps.com/) Unoffical API.

Since the API is unofficial it could in theory change at any time. In practice though breaking changes are rare.


## Setup:

Simply install the library using `pip`.


## Usage

### Authentication

To authenticate to the primary servers just supply a username and password.

```python
import screepsapi
USER = "MyUsername"
PASSWORD = "TimeTravelingSecretAgentForHire"
api = screepsapi.API(USER, PASSWORD)
```


It is also possible to access private servers with the `host` and `secure` parameters.

```python
import screepsapi
USER = "MyUsername"
PASSWORD = "TimeTravelingSecretAgentForHire"
api = screepsapi.API(USER, PASSWORD, host="server1.screepspl.us:443", secure=True)
```

Note that by default private servers do not use SSL and all traffic is unencrypted.

### API

The API itself is a simple REST-based API. Each method in the api library corresponds to a different endpoint for the API.

The best way to discover functionality is to read through the library itself.

#### Console Example

```python
import screepsapi
USER = "MyUsername"
PASSWORD = "TimeTravelingSecretAgentForHire"
api = screepsapi.API(USER, PASSWORD, host="server1.screepspl.us:443", secure=True)

# Run "Game.time" on shard1 via the console
api.console('Game.time', shard='shard1')
```

#### User Information Example

```python
import screepsapi
USER = "MyUsername"
PASSWORD = "TimeTravelingSecretAgentForHire"
api = screepsapi.API(USER, PASSWORD, host="server1.screepspl.us:443", secure=True)

# Find the GCL for `tedivm`
user = api.user_find("tedivm")
print user["user"]["gcl"]
```

### Socket

Screeps provides a sizable amount of data over a websocket. This includes console data and room details.

The best way to utilize the socket is to extend `screepsapi.Socket` and override the various abstract functions.
