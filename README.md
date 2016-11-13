# screepsapi

## Setup:
* If you don't have pip, [install pip](https://pip.pypa.io/en/latest/installing/#install-or-upgrade-pip).
  * _Why don't you have pip._
* Install the package requirements (currently request and websocket) if you don't have them.

## Example use:

```
import screepsapi
user = "MyUsername"
password = "TimeTravelingSecretAgentForHire"

api = screepsapi.API(user, password)
user = api.user_find("tedivm")
print user["user"]["gcl"]
```

## Private servers:

Specify 'host' and 'secure' to connect to a private server. local servers
don't seem to have TLS, so default is off. Be wary if connecting over the
internet to your private server!

```
api = screepsapi.API(user, password, host="locahost:21025")
