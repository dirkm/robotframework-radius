RadiusLibrary
=============
Scope:            test case
Named arguments:  supported

``RadiusLibrary`` is a test library providing keywords for handling the RADIUS
protocol.
This library uses the pyrad package for RADIUS protocol handling.
Pyrad source code is located at https://github.com/wichert/pyrad. The library
supports the creation of RADIUS clients and servers, and supports
authentication, accounting and change of authorization requests.
Multiple client and server sessions can be create through the use the `alias`
parameter.
= Examples =
== Client ==
Example of client authentication session:
| `Create Client`         | server=127.0.0.1 | port=1812 | secret=mysecret |
| `Create Access Request` |
| `Add Request Attribute` | User-Name         | subscriber       |
| `Add Request Attribute` | User-Password     | mypass           |
| `Add Request Attribute` | Acct-Session-Id   | someid           |
| `Send Request` |
| `Receive Access Accept` | timeout=5.0 |
| `Response Should Contain Attribute` | Framed-IP-Address | 10.0.0.100 |

Example of client accounting session:
| `Create Client` | server=127.0.0.1 | port=1813 | secret=mysecret |
| `Create Access Request` |
| `Create Accounting Request` |
| `Add Request Attribute` | User-Name         | subscriber       |
| `Add Request Attribute` | Acct-Session-Id   | someid           |
| `Add Request Attribute` | Acct-Status-Type  | Start            |
| `Send Request` |
| `Receive Accounting Response` |

== Server ==
Example of server session:
| `Create Server`          | server=127.0.0.1 | port=1812 | secret=mysecret |
| `Receive Access Request` |
| `Request Should Contain Attribute` | User-Name | subscriber |
| `Request Should Contain Attribute` | User-Password | mypass |
| `Request Should Contain Attribute` | Acct-Session-Id |
| `Create Access Accept` |
| `Add Request Attribute`  | Framed-IP-Address | 10.0.0.100 |
| `Send Response` |

Add Request Attribute
---------------------
Arguments:  [key, value, alias=None]

Adds attribute to the created RADIUS request.

- ``key:``   RADIUS attribute identifier, ie User-Name, Acct-Session-Id.
- ``value:`` RADIUS attribute value.
- ``alias:`` alias to identify the client session to use.

Add Response Attribute
----------------------
Arguments:  [key, value, alias=None]

Adds attribute to the created RADIUS response.

- ``key:``   RADIUS attribute identifier, ie User-Name, Acct-Session-Id.
- ``value:`` RADIUS attribute value.
- ``alias:`` alias to identify the client session to use.

Create Access Accept
--------------------
Arguments:  [alias=None]

Creates an access accept response.

- ``alias:`` alias to identify the session to use.

Create Access Reject
--------------------
Arguments:  [alias=None]

Creates an access accept.

- ``alias:`` alias to identify the session to use.

Create Access Request
---------------------
Arguments:  [alias=None]

Creates an access request.

- ``alias:`` alias to identify the session to use.

Create Accounting Request
-------------------------
Arguments:  [alias=None]

Creates an accounting request.

- ``alias:`` alias to identify the session to use.

Create Accounting Response
--------------------------
Arguments:  [alias=None]

Creates an accounting response.

- ``alias:`` alias to identify the session to use.

Create Client
-------------
Arguments:  [alias, address, port, secret, raddict=dictionary,
            authenticator=True]

Create Client: create a RADIUS session to a server.

- ``alias:`` Alias to identify the session to use.

- ``address:`` IP address of the RADIUS server.

- ``port:`` IP port of the RADIUS server.

- ``secret:`` RADIUS secret.

- ``raddict:`` Path to RADIUS dictionary.

- ``authenticator:`` Authenticator boolean switch.

Examples:
| Create Client | auth_client | 127.0.0.1 | 1812 | mysecret |
|
| Create Client | acct_client | 127.0.0.1 | 1813 | mysecret |
dictionary=mydict   |
| Create Client |  coa_client | 127.0.0.1 | 3799 | mysecret |
authenticator=False |

The next step after creating a client is to create a request, using the
`Create Access Request` keyword for example.
After creating a client, it is ready to send requests using the `Receive
Access Request` keyword for example.

Create Coa Ack
--------------
Arguments:  [alias=None]

Creates a coa ack response.

- ``alias:`` alias to identify the session to use.

Create Coa Nack
---------------
Arguments:  [alias=None]

Creates a coa nack response.

- ``alias:`` alias to identify the session to use.

Create Coa Request
------------------
Arguments:  [alias=None]

Creates an coa request.

- ``alias:`` alias to identify the session to use.

Create Server
-------------
Arguments:  [alias=None, address=127.0.0.1, port=0, secret=secret,
            raddict=dictionary]

Creates a RADIUS server.

- ``alias:`` Alias to identify the servr session to use.

- ``address:`` IP address of the RADIUS server.

- ``port:`` IP port of the RADIUS server.

- ``secret:`` RADIUS secret.

- ``raddict:`` Path to RADIUS dictionary.

Examples:
| Create Server | auth_server | 127.0.0.1 | 1812 | mysecret |
|
| Create Server | acct_server | 127.0.0.1 | 1813 | mysecret |
dictionary=mydict   |
| Create Server |  coa_server | 127.0.0.1 | 3799 | mysecret |
|

After creating a server it is ready to receive requests using the `Receive
Access Request` keyword for example.

Receive Access Accept
---------------------
Arguments:  [alias=None, timeout=10.0]

Receives an access accept.

- ``alias:`` alias to identify the session to use.
- ``timeout:`` Sets receive timeout in seconds(float).

Receive Access Reject
---------------------
Arguments:  [alias=None, timeout=10.0]

Receives an access reject.

- ``alias:`` alias to identify the session to use.
- ``timeout:`` Sets receive timeout in seconds(float).

Receive Access Request
----------------------
Arguments:  [alias=None, timeout=10.0]

Receives an access request.

- ``alias:`` alias to identify the session to use.
- ``timeout:`` Sets receive timeout in seconds(float).

Receive Accounting Request
--------------------------
Arguments:  [alias=None, timeout=10.0]

Receives an accounting request.

- ``alias:`` alias to identify the session to use.
- ``timeout:`` Sets receive timeout in seconds(float).

Receive Accounting Response
---------------------------
Arguments:  [alias=None, timeout=10.0]

Receives an accounting response.

- ``alias:`` alias to identify the session to use.
- ``timeout:`` Sets receive timeout in seconds(float).

Receive Coa Ack
---------------
Arguments:  [alias=None, timeout=10.0]

Receives a coa ack response.

- ``alias:`` alias to identify the session to use.
- ``timeout:`` Sets receive timeout in seconds(float).

Receive Coa Nack
----------------
Arguments:  [alias=None, timeout=10.0]

Receives a coa nack response.

- ``alias:`` alias to identify the session to use.
- ``timeout:`` Sets receive timeout in seconds(float).

Receive Coa Request
-------------------
Arguments:  [alias=None, timeout=10.0]

Receives a coa request.

- ``alias:`` alias to identify the session to use.
- ``timeout:`` Sets receive timeout in seconds(float).

Request Should Contain Attribute
--------------------------------
Arguments:  [key, val=None, alias=None]

Checks RADIUS request if specified `key`, or `key value` exists.

If not, An error will be raised.

- ``key:``   RADIUS attribute identifier, ie Framed-IP-Address.
- ``value:`` RADIUS attribute value.
- ``key:`` Alias to identify the servr session to use.

Response Should Contain Attribute
---------------------------------
Arguments:  [key, val=None, alias=None]

Checks RADIUS response  if specified `key`, or `key value` exists.

If not, An error will be raised.

- ``key:``   RADIUS attribute identifier, ie Framed-IP-Address.
- ``value:`` RADIUS attribute value.
- ``key:`` Alias to identify the servr session to use.

Send Request
------------
Arguments:  [alias=None]

Sends RADIUS client request using session specified by `alias`.

- ``key:``   RADIUS attribute identifier, ie User-Name, Acct-Session-Id.
- ``value:`` RADIUS attribute value.
- ``alias:`` alias to identify the client session to use.

Send Response
-------------
Arguments:  [alias=None]

Sends RADIUS server resoponse using session specified by `alias`.

- ``alias:`` alias to identify the client session to use.
