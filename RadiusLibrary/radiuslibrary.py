# Copyright 2016 Michael van Slingerland - Deviousops
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import select
import socket
import six
import robot
from robot.libraries.BuiltIn import BuiltIn
from pyrad import packet, dictionary, tools

# Default receive timeout
TIMEOUT = 10.0

# Default Radius dictionary file
DEFAULT_DICT = 'dictionary'

class RadiusLibrary(object):
    """``RadiusLibrary`` is a test library providing keywords for handling the RADIUS protocol.
    This library uses the pyrad package for RADIUS protocol handling.
    Pyrad source code is located at https://github.com/wichert/pyrad. The library supports the creation of RADIUS clients and servers, and supports authentication, accounting and change of authorization requests.
    Multiple client and server sessions can be create through the use the `alias` parameter.
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
    """

    ROBOT_LIBRARY_SCOPE = 'TEST CASE'

    def __init__(self):
        self._client = robot.utils.ConnectionCache('No Clients Created')
        self._server = robot.utils.ConnectionCache('No Servers Created')
        self.builtin = BuiltIn()

    def create_client(self, alias, address, port,
                      secret, raddict=DEFAULT_DICT,
                      authenticator=True):
        """ Create Client: create a RADIUS session to a server.

        - ``alias:`` Alias to identify the session to use.

        - ``address:`` IP address of the RADIUS server.

        - ``port:`` IP port of the RADIUS server.

        - ``secret:`` RADIUS secret.

        - ``raddict:`` Path to RADIUS dictionary.

        - ``authenticator:`` Authenticator boolean switch.

        Examples:
        | Create Client | auth_client | 127.0.0.1 | 1812 | mysecret |                     |
        | Create Client | acct_client | 127.0.0.1 | 1813 | mysecret | dictionary=mydict   |
        | Create Client |  coa_client | 127.0.0.1 | 3799 | mysecret | authenticator=False |

        The next step after creating a client is to create a request, using the `Create Access Request` keyword for example.
        After creating a client, it is ready to send requests using the `Receive Access Request` keyword for example.

        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', 0))
        sock.settimeout(3.0)
        sock.setblocking(0)
        request = robot.utils.ConnectionCache('No Client Sessions Created')
        response = robot.utils.ConnectionCache('No Client Response Created')
        session = {'sock': sock,
                   'address': str(address),
                   'port': int(port),
                   'secret': six.b(str(secret)),
                   'dictionary': dictionary.Dictionary(raddict),
                   'authenticator': authenticator,
                   'request': request,
                   'response': response}

        self._client.register(session, alias=alias)
        return session

    def _create_request(self, alias, code):
        client = self._get_session(self._client,alias)
        secret = client['secret']
        dictionary = client['dictionary']

        if code == packet.AccessRequest:
          request = packet.AuthPacket(code=code, secret=secret,
                                      dict=dictionary)

        elif code in [packet.AccountingRequest, packet.CoARequest, packet.DisconnectRequest]:
          request = packet.AcctPacket(code=code, secret=secret,
                                      dict=dictionary)

        client['request'].register(request, str(request.id))
        return request

    def create_access_request(self,alias=None):
        """ Creates an access request.

        - ``alias:`` alias to identify the session to use.

        """
        return self._create_request(alias,packet.AccessRequest)

    def create_accounting_request(self,alias=None):
        """ Creates an accounting request.

        - ``alias:`` alias to identify the session to use.

        """
        return self._create_request(alias,packet.AccountingRequest)

    def create_coa_request(self,alias=None):
        """ Creates an coa request.

        - ``alias:`` alias to identify the session to use.

        """
        return self._create_request(alias,packet.CoARequest)

    def create_disconnect_request(self,alias=None):
        """ Creates a disconnect request.

        - ``alias:`` alias to identify the session to use.

        """
        return self._create_request(alias,packet.DisconnectRequest)

    def _add_attribute(self, cache, key, value, alias):
        key = str(key)
        if isinstance(value, unicode):
            value = str(value)
        client = self._get_session(cache,alias)
        if cache == self._client:
          packet = client['request'].get_connection(alias)
        if cache == self._server:
          packet = client['response'].get_connection(alias)
        attr_dict_item = packet.dict.attributes[key]

        if attr_dict_item.type == 'integer':
            if attr_dict_item.values.HasForward(value) == False:
              value = int(value)
        elif attr_dict_item.type == 'string':
            value = str(value)
        if attr_dict_item.encrypt == 1:
            value = packet.PwCrypt(value)
        packet.AddAttribute(key,value)

    def add_request_attribute(self, key, value, alias=None):
        """Adds attribute to the created RADIUS request.

        - ``key:``   RADIUS attribute identifier, ie User-Name, Acct-Session-Id.
        - ``value:`` RADIUS attribute value.
        - ``alias:`` alias to identify the client session to use.

        """
        return self._add_attribute(self._client, key, value, alias)

    def send_request(self, alias=None):
        """Sends RADIUS client request using session specified by `alias`.

        - ``key:``   RADIUS attribute identifier, ie User-Name, Acct-Session-Id.
        - ``value:`` RADIUS attribute value.
        - ``alias:`` alias to identify the client session to use.

        """
        client = self._get_session(self._client,alias)
        request = client['request'].get_connection(alias)
        pdu =  request.RequestPacket()
        client['sock'].sendto(pdu, (client['address'], client['port']))
        return dict(request)

    def _receive_response(self,alias,code,timeout):
        client = self._get_session(self._client, alias)
        ready = select.select([client['sock']], [], [], float(timeout))

        pkt = None
        if ready[0]:
            data, addr = client['sock'].recvfrom(1024)
            pkt = packet.Packet(secret=client['secret'], packet=data,
            dict=client['dictionary'])
            client['response'].register(pkt,str(pkt.id))

            self.builtin.log(pkt.keys())
            if pkt.code != code:
                # TODO: name packet code instead of id.
                self.builtin.log('Expected {0}, received {1}'.format(code, pkt.code))
                raise Exception("received {}".format(pkt.code))
        if pkt is None:
            raise Exception("Did not receive any answer")

        return pkt

    def receive_access_accept(self, alias=None, timeout=TIMEOUT):
        """ Receives an access accept.

        - ``alias:`` alias to identify the session to use.
        - ``timeout:`` Sets receive timeout in seconds(float).

        """
        return self._receive_response(alias, packet.AccessAccept, timeout)

    def receive_access_reject(self, alias=None, timeout=TIMEOUT):
        """ Receives an access reject.

        - ``alias:`` alias to identify the session to use.
        - ``timeout:`` Sets receive timeout in seconds(float).

        """
        return self._receive_response(alias, packet.AccessReject, timeout)

    def receive_accounting_response(self, alias=None, timeout=TIMEOUT):
        """ Receives an accounting response.

        - ``alias:`` alias to identify the session to use.
        - ``timeout:`` Sets receive timeout in seconds(float).

        """
        return self._receive_response(alias, packet.AccountingResponse, timeout)

    def receive_coa_ack(self, alias=None, timeout=TIMEOUT):
        """ Receives a coa ack response.

        - ``alias:`` alias to identify the session to use.
        - ``timeout:`` Sets receive timeout in seconds(float).

        """
        return self._receive_request(alias, packet.CoARequest, timeout)

    def receive_coa_nack(self, alias=None, timeout=TIMEOUT):
        """ Receives a coa nack response.

        - ``alias:`` alias to identify the session to use.
        - ``timeout:`` Sets receive timeout in seconds(float).

        """
        return self._receive_request(alias, packet.CoARequest, timeout)

    def response_should_contain_attribute(self, key, val=None, alias=None):
        """ Checks RADIUS response  if specified `key`, or `key value` exists.

        If not, An error will be raised.

        - ``key:``   RADIUS attribute identifier, ie Framed-IP-Address.
        - ``value:`` RADIUS attribute value.
        - ``key:`` Alias to identify the servr session to use.

        """
        return self._should_contain_attribute(self._client,key,val,alias)


    # Server section
    def create_server(self, alias=None, address='127.0.0.1', port=0, secret='secret', raddict=DEFAULT_DICT):
        """ Creates a RADIUS server.

        - ``alias:`` Alias to identify the servr session to use.

        - ``address:`` IP address of the RADIUS server.

        - ``port:`` IP port of the RADIUS server.

        - ``secret:`` RADIUS secret.

        - ``raddict:`` Path to RADIUS dictionary.

        Examples:
        | Create Server | auth_server | 127.0.0.1 | 1812 | mysecret |                     |
        | Create Server | acct_server | 127.0.0.1 | 1813 | mysecret | dictionary=mydict   |
        | Create Server |  coa_server | 127.0.0.1 | 3799 | mysecret |                     |

        After creating a server it is ready to receive requests using the `Receive Access Request` keyword for example.

        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((address, int(port)))
        #sock.settimeout(3.0)
        sock.setblocking(0)
        request = robot.utils.ConnectionCache('No Server Requests Created')
        response = robot.utils.ConnectionCache('No Server Responses Created')
        server = {'sock': sock,
                  'secret': six.b(str(secret)),
                  'dictionary': dictionary.Dictionary(raddict),
                  'request':request,
                  'response':response}

        self._server.register(server, alias=alias)
        return server

    def _receive_request(self,alias,code,timeout):
        server = self._get_session(self._server, alias)
        ready = select.select([server['sock']], [], [], float(timeout))

        pkt = None
        if ready[0]:
            data, addr = server['sock'].recvfrom(1024)
            pkt = packet.Packet(secret=server['secret'], packet=data,
                                    dict=server['dictionary'])
            server['request'].register(pkt,str(pkt.id))

            self.builtin.log(pkt.code)
            if pkt.code != code:
                self.builtin.log('Expected {0}, received {1}'.format(code, pkt.code))
                raise Exception("received {}".format(pkt.code))
        if pkt is None:
            raise Exception("Did not receive any answer")
        pkt.addr = addr
        return pkt

    def request_should_contain_attribute(self, key, val=None, alias=None):
        """ Checks RADIUS request if specified `key`, or `key value` exists.

        If not, An error will be raised.

        - ``key:``   RADIUS attribute identifier, ie Framed-IP-Address.
        - ``value:`` RADIUS attribute value.
        - ``key:`` Alias to identify the servr session to use.

        """
        return self._should_contain_attribute(self._server,key,val,alias)

    def _create_response(self, alias, code):
        session = self._get_session(self._server,alias)
        request = session['request'].get_connection(alias)
        reply = request.CreateReply()
        reply.code = code
        session['response'].register(reply,str(reply.code))
        #todo: deregister request
        return reply

    def create_access_accept(self, alias=None):
        """ Creates an access accept response.

        - ``alias:`` alias to identify the session to use.

        """
        return self._create_response(alias,packet.AccessAccept)

    def create_access_reject(self, alias=None):
        """ Creates an access accept.

        - ``alias:`` alias to identify the session to use.

        """
        return self._create_response(alias,packet.AccessReject)

    def create_accounting_response(self, alias=None):
        """ Creates an accounting response.

        - ``alias:`` alias to identify the session to use.

        """
        return self._create_response(alias,packet.AccountingResponse)

    def create_coa_ack(self, alias=None):
        """ Creates a coa ack response.

        - ``alias:`` alias to identify the session to use.

        """
        return self._create_response(alias,packet.CoAACK)

    def create_coa_nack(self, alias=None):
        """ Creates a coa nack response.

        - ``alias:`` alias to identify the session to use.

        """
        return self._create_response(alias,packet.CoANAK)

    def create_disconnect_ack(self, alias=None):
        """ Creates a disconnect ack response.

        - ``alias:`` alias to identify the session to use.

        """
        return self._create_response(alias,packet.DisconnectACK)

    def create_disconnect_nack(self, alias=None):
        """ Creates a disconnect nack response.

        - ``alias:`` alias to identify the session to use.

        """
        return self._create_response(alias,packet.DisconnectNAK)
    def add_response_attribute(self, key, value, alias=None):
        """Adds attribute to the created RADIUS response.

        - ``key:``   RADIUS attribute identifier, ie User-Name, Acct-Session-Id.
        - ``value:`` RADIUS attribute value.
        - ``alias:`` alias to identify the client session to use.

        """
        return self._add_attribute(self._server, key, value, alias)

    def send_response(self, alias=None):
        """Sends RADIUS server resoponse using session specified by `alias`.

        - ``alias:`` alias to identify the client session to use.

        """
        server = self._get_session(self._server, alias)
        request = server['request'].get_connection(alias)
        response = server['response'].get_connection(alias)
        pdu =  response.ReplyPacket()
        server['sock'].sendto(pdu, request.addr)
        return request

    def receive_accounting_request(self, alias=None, timeout=TIMEOUT):
        """ Receives an accounting request.

        - ``alias:`` alias to identify the session to use.
        - ``timeout:`` Sets receive timeout in seconds(float).

        """
        return self._receive_request(alias, packet.AccountingRequest, timeout)

    def receive_coa_request(self, alias=None, timeout=TIMEOUT):
        """ Receives a coa request.

        - ``alias:`` alias to identify the session to use.
        - ``timeout:`` Sets receive timeout in seconds(float).

        """
        return self._receive_request(alias, packet.CoARequest, timeout)

    def receive_disconnect_request(self, alias=None, timeout=TIMEOUT):
        """ Receives a disconnect request.

        - ``alias:`` alias to identify the session to use.
        - ``timeout:`` Sets receive timeout in seconds(float).

        """
        return self._receive_request(alias, packet.DisconnectRequest, timeout)

    def receive_access_request(self, alias=None, timeout=TIMEOUT):
        """ Receives an access request.

        - ``alias:`` alias to identify the session to use.
        - ``timeout:`` Sets receive timeout in seconds(float).

        """
        return self._receive_request(alias, packet.AccessRequest, timeout)

    def _get_session(self, cache, alias):
        # Switch to related client alias
        if alias:
            return cache.switch(alias)
        else:
            return cache.get_connection()

    def _should_contain_attribute(self, cache, key, val, alias):
        session=self._get_session(cache, alias)
        request = None
        if cache == self._client:
            request = session['response'].get_connection(alias)
        elif cache == self._server:
            request = session['request'].get_connection(alias)
        else:
            raise BaseException('No match for cache')
        if not val:
            if str(key) in request:
                return True
            else:
                raise BaseException('Key {} not found in {}'.format(key,str(request.keys())))
        else:

            if str(key) in request and val in request[str(key)]:
                return
            else:
                raise BaseException('value "{}" not in {}'.format(val,request[str(key)]))
