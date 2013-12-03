from socket import *
import struct
import threading
from time import ctime
import traceback

HOST = ''
PORT = 21567
ADDR = (HOST, PORT)
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
    
#w = ClientProtocol()
#w.makeConnection()

#w.sendUserInfo('jane')
#w.dataRecived()
#w.sendDialog('HAHHAHAHAH')
#w.dataRecived()
#w.lostConnection()

class PeerToPeer(object):
  def __init__(self, serverport, serverhost):
    self.shutdown = False
    self.port = 21567
    self.host = ''
    self.serverport = serverport
    self.serverhost = serverhost
    self.peers = {}
    self.peerLock = threading.Lock()
    
  def makeSeverSocket(self, port):
    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1 )
    s.bind( ( '', port ) )
    s.listen(5)
    return s
  
  def addPeer(self, host, port):
    if not self.peers.has_key(host):
      self.peers[host] = port
    else:
      print 'The peer %s has already added!'%host
    
  def getPeer(self, host):
    if self.peers.has_key(host):
      return (host, self.peers[host])
  
  def recieveHandler(self, clientsock):
    host, port = clientsock.getpeername()
    peerconn = PeerConnection(host, port)
    
    try:
      msgtype, msgdata = peerconn.recvData()
      if msgtype == "str":
        print msgdata
        self.msg = msgdata
        msg = raw_input('Input what you want>')
        sendDataToPeer(host, port, 'str', msg)
    except KeyboardInterrupt:
      raise
    
    return (msgtype, msgdata)
  
  def sendDataToPeer(self, server, port, mstype, msg):
    print 'Sending...'
    peerconn = PeerConnection(server, port)
    #msgreply = []
    if peerconn.connect:
      peerconn.sendData(mstype, msg)
      peerconn.close()
    else:
      print 'Connections failed!'
    
  
  def checkPeerAlive(self):
    todelete = []
    for host in self.peers.keys():
      port = self.peers[host]
      peerconn = PeerConnection(host, port)
      if peerconn.connect:
        pass
      else:
        todelete.append(host)
      
    self.peerLock.acquire()
    try:
      for host in todelete:
        if self.peers.has_key(host):
          del self.peers[host]

    finally:
      self.peerLock.release()
  
  
  def mainloop(self):
    s = self.makeSeverSocket(self.port)
    
    while not self.shutdown:
      try:
        print '%s listening for connections' %self.port
        clientsock, clientaddr = s.accept()
        
        t = threading.Thread(target = self.recieveHandler,
                      args=[clientsock])
        t.start()
      except KeyboardInterrupt:
        print 'KeyboardInterrupt terminated'
        self.shutdown = True
      
    
    s.close()

class PeerConnection(object):
  def __init__(self, host, port):
    self.port = port
    self.host = host
    try:
      self.s = socket(AF_INET, SOCK_STREAM)
      print 'connect socket is building'
      self.s.connect((host, port))
      self.connect = True
    except error, (value, message):
      if self.s:
        self.s.close()
      self.connect = False
  
  def recvData(self):
    msg = ''
    if self.connect:
      msg = self.s.recv(BUFSIZ)
    
    data = msg.split('^^^')
    if len(data) == 3:
      self.msgtype = data[0]
      self.msg = data[1]
      self.msgdate = data[2]
    
      if self.msgtype == 'str':
        print "recieve message from peer %s %s" %(self.msg, self.msgdate)
      
      return (self.msgtype, self.msg)
    
  def sendData(self, msgtype, msg):
    data = []
    data.append(msgtype)
    data.append(msg)
    data.append(str(ctime()))
    sstr = '^^^'.join(data)
    
    try:
      self.s.send(sstr)
    
    except KeyboardInterrupt:
      print 'Send failed!'
  
  def close(self):
    self.s.close()
      

class ControlFactory(object):
  def __init__(self, serverhost, serverport):
    self.peer = PeerToPeer(serverhost,serverport)
  
  def makePeerService(self):
    self.t = threading.Thread(target=self.peer.mainloop, args=[])
    self.t.start()
  
  def sendData(self, host, port):
    self.peer.addPeer(host, port)
    msg = raw_input('input what you want>')
    ret = self.peer.sendDataToPeer(host, port, 'str', msg)
    print 'The returned message is %s'%ret
    self.peer.checkPeerAlive()


if __name__ == "__main__":
  w1 = ControlFactory("192.168.1.130", 21567)
  print "Here"
  w1.makePeerService()
  w1.sendData('', 21567)
  
    
  
  
    
