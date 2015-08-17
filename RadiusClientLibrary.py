from pyrad import packet,dictionary
import socket
import six
import select

class RadiusClientLibrary(object):
    def __init__(self,addr,port,secret):
        self.addr = (addr, int(port))
        self.attributes = []
        self.secret = str(secret)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(1.5)
        self.sock.setblocking(0)

    def add_attribute(self,name,value):
        if type(name) == unicode:
            name = str(name)
        self.attributes.append((name,value))

    def send_access_request(self):
        p = packet.AuthPacket(code=1, secret=six.b(self.secret), id=124,dict=dictionary.Dictionary("dictionary"))
        
        for attr in self.attributes:
            if attr[0] == 'User-Password':
                p[attr[0]] = p.PwCrypt(attr[1])
            else:
                p[attr[0]] = attr[1]

        raw = p.RequestPacket()
       
        self.sock.sendto(raw,self.addr)

    def receive_access_accept(self):
        ready = select.select([self.sock], [], [], 1)
        if ready[0]:
            data, addr = self.sock.recvfrom(1024)
            p = packet.Packet(secret=self.secret,packet=data,dict=dictionary.Dictionary("dictionary"))
            
            if p.code != packet.AccessAccept:
                raise Exception("Did not receive Access Accept")
        self.response = p

    def response_attribute_equals(self,k,v):
        if type(k) == unicode:
          k = str(k)
        if type(v) == unicode:
          v = str(v)
        if  k not in self.response:
          raise Exception('Attribute {0} does not exist'.format(k))
        if type(v) == list:
          if v != self.response[k]:
            raise Exception('{0} != {1}'.format(self.response[k], v))

        else:
          if v not in self.response[k]:
            raise Exception('{0} not in  {1}'.format(self.response[k], v))

    def receive_access_reject(self):
        ready = select.select([self.sock], [], [], 1)
        if ready[0]:
            data, addr = self.sock.recvfrom(1024)
            p = packet.Packet(secret=self.secret,packet=data,dict=dictionary.Dictionary("dictionary"))
            
            if p.code != packet.AccessReject:
                raise Exception("Did not receive Access Reject")
        self.response = p

    def send_accounting_request(self):
        p = packet.AcctPacket(secret=self.secret, id=124,dict=dictionary.Dictionary("dictionary.rfc2865"))
        print self.attributes
        for attr in self.attributes:
            p[attr[0]] = attr[1]
        print p
        raw = p.RequestPacket()
       
        self.sock.sendto(raw,self.addr)

if __name__ == '__main__':
  r = RadiusClientLibrary('172.17.0.1',1813,'bras1001')
  r.add_attribute('User-Name','mike')
  r.send_accounting_request()
