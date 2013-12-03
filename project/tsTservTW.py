#!/usr/bin/env python

#using Twisted, if you dont have, please install first

from twisted.internet import protocol, reactor
from time import ctime

PORT = 21567
usernames = set()
login = {}

class TSServProtocol(protocol.Protocol):
    
  def connectionMade(self):
    clnt = self.clnt = self.transport.getPeer().host
    print '...connected from:', clnt

  def dataReceived(self, data):
    print 'received!'
    #judge data type
    d = data.split('^^^')
    print d
    print type(d)
    
    if len(d) == 2:
      if d[1] and d[0] == 'Name':
        print usernames
        print login
        res =  d[1] in usernames
        #print res
        
        if res:
          self.transport.write("False^^^username")
        else:
          usernames.add(d[1])
          print usernames
          login[self.clnt] = d[1]
          self.transport.write("True^^^username")
    else:
      self.transport.write('[%s] %s %s' % (
        ctime(), self.login[self.clnt] ,data))
    
factory = protocol.Factory()
factory.protocol = TSServProtocol
print 'Waiting for connections..'
reactor.listenTCP(PORT, factory)
reactor.run()