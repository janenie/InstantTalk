from socket import *
import struct
import threading
from time import ctime
import traceback
import sys
import random

HOST = '127.0.0.1'
LISTEN_PORT_SELF = 22345
LISTEN_PORT_OTHER = 54321
# ADDR = (HOST, PORT)
BUFSIZ = 1024

class ClientProtocol(object):
  '''Protocol for sending message'''
  def __init__(self):
    self.msg = []
    self.login = False
    self.connected = False
    
  def makeConnection(self):
    try:
      self.tcpCliSock = socket(AF_INET, SOCK_STREAM)
      self.tcpCliSock.connect(ADDR)
      self.connected = True
    except error, (value, message):
      if self.tcpCliSock:
        self.tcpCliSock.close()
      self.connected = False
  
  def lostConnection(self):
    self.tcpCliSock.close()
  
  def sendDialog(self, msg):
    self.tcpCliSock.send(msg)
  
  def sendUserInfo(self, msg):
    msg = str(msg)
    self.msg = ['Name', msg]
    s = '^^^'.join(self.msg)
    if msg:
      print s
      self.tcpCliSock.send(s)
    else:
      pass
      
  def getPermission(self, msg):
    if msg == 'True':
      self.login = True
      print 'Login succeed!'
    else:
      self.login = False
      print 'Login failed, change a name'
  
  def dataRecived(self):
    data = self.tcpCliSock.recv(BUFSIZ)
    d = data.split('^^^')
    if len(d) > 1:
      res = d[0]
      self.getPermission(res)
    else:
      self.dialog = data
      print data
  
  def getDialog(self):
    return self.dialog
    
  def getLogin(self):
    return self.login
    
  def testConnected(self):
    return self.connected
    
class PeerToPeer(object):
  def __init__(self):
    self.port = LISTEN_PORT_SELF
    self.host = HOST
    self.peers = {}
    self.peer_connected = {}
  
  def makeSeverSocket(self, port):
    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind( ( '', port ) )
    s.listen(5)
    return s
  
  def receiveHandler(self, clientsock):
    host, port = clientsock.getpeername()
    if clientsock:
      datas= clientsock.recv(BUFSIZ)
      msg = datas.split('^^^')
      if len(msg) == 3:
        self.msgtype = msg[0]
        self.msgdata = msg[1]
        self.msgdate = msg[2]
      
      reply = raw_input('Reply to sender>')
      self.sendDataToPeer(host, LISTEN_PORT_OTHER)
    
  def sendDataToPeer(self, host, port):
    if not self.peer_connected.has_key((host, port)):
      self.peer_connected[(host, port)] = PeerConnection(host, port)
    
    peerconn = self.peer_connected[(host, port)]
    if peerconn.connect:
      msg = raw_input('sending data>')
      peerconn.sendData(msg)
    
    else:
      print 'Connection failed'
      
  
  def addPeer(self, host, port):
    if not self.peers.has_key(host):
      self.peers[host] = port
    else:
      print 'The peer %s has already added!'%host
    
  def getPeer(self, host):
    if self.peers.has_key(host):
      return (host, self.peers[host])
  
  def mainloop(self):
    print 'mainloop'
    s = self.makeSeverSocket(self.port)
    
    # while not self.shutdown:
    while True:
      # print '%s listening for connections' %self.port
      print 'Listening on ', LISTEN_PORT_SELF
      clientsock, clientaddr = s.accept()
      t = threading.Thread(target = self.recieveHandler,
                      args=[clientsock])
      t.start()
      
    s.close()
    
class PeerConnection(object):
  def __init__(self, host, port):
    self.port = port
    self.host = host
    self.s = socket(AF_INET, SOCK_STREAM)
    self.s.connect((host, port))
    self.connect = True
  
  def sendData(self, msg):
    data = ['str', msg, ctime()]
    s = '^^^'.join(data)
    
    self.s.send(s)
  
  def close(self):
    self.s.close()
    

class ControlFactory(object):
  def __init__(self):
    self.peer = PeerToPeer()
  
  def makePeerService(self):
    self.t = threading.Thread(target=self.peer.mainloop, args=[])
    self.t.start()
  
  def sendData(self, host, port):
    self.peer.addPeer(host, port)
    msg = raw_input('input what you want>')
    self.peer.sendDataToPeer(host, port)
    # self.peer.checkPeerAlive()
    

if __name__ == "__main__":
  if not sys.argv[-1] == 'recv':
    LISTEN_PORT_OTHER, LISTEN_PORT_SELF = LISTEN_PORT_SELF, LISTEN_PORT_OTHER

  w1 = ControlFactory()
  print "Here"
  w1.makePeerService()
  if not sys.argv[-1] == 'recv':
      w1.sendData(HOST, LISTEN_PORT_OTHER)

    
    