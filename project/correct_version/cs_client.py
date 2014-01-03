#!/usr/bin/env python
import socket
import threading
import thread
from time import ctime, sleep
from format import Message
import sys
import random
import traceback

HOST = '127.0.0.1'
PORT = 54321
ADDR = (HOST, PORT)
CLIENTPORT = 22345
BUFSIZ = 2048

class ClientProtocolForCS(object):
    '''Sending message to server'''
    def __init__(self):
        self.login = False
        self.msg = Message()
        self.connected = False
        self.host = str(socket.gethostbyname(socket.gethostname()))
        self.handshaked = False
        #sprint self.host
    
    def makeConnection(self):
        try:
            self.tcpCliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcpCliSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.tcpCliSock.connect(ADDR)
            self.connected = True
        except socket.error, (value, message):
            if self.tcpCliSock:
                self.tcpCliSock.close()
            self.connected = False
    
    def lostConnection(self):
        if self.connected == True:
            self.tcpCliSock.close()
    
    def sendMessage(self, types, data = None):
        msg = ''
        types = str(types)
        #print "passed type is ", types
        if types == "handshake":
            msg = self.msg.handshakeMsg(self.host)
            #print "here ", msg
            
        if types == "login":
            #print 'send!'
            username = data[0]
            port = data[1]
            msg = self.msg.loginUserMsg(username, port)
            
        if types == "requestOnlineUsers":
            msg = self.msg.requestOnlineUsersMsg()
            
        if types == "talkToAll":
            username = data[0]
            dialog = data[1]
            msg = self.msg.userTalkToAllMsg(username, dialog)
        
        if types == "leave":
            msg = self.msg.userLeaveMsg(data)
        
        if types == "beat":
            msg = self.msg.sendBeatToServerMsg(data)
        
        if msg != '':
            self.tcpCliSock.send(msg)
    
    def getMessage(self):
        data = self.tcpCliSock.recv(BUFSIZ)
        lines = data.split('\n')
        requestline = lines[0].split(' ')
        ret_msg = ''
        #print 'Recieved'
        #judge type
        if 'MINET' in requestline:
            self.handshaked = True
            ret_msg = "handshakeTrue"
        
        if 'STATUS' in requestline:
            #infos = requestline.split(' ')
            if requestline[2] == '1':
                self.login = True
                ret_msg = "loginTrue"
            else:
                self.login = False
                ret_msg = "loginFalse"
        
        if 'CSMESSAGE' in requestline:
            content = lines[3]
            username = (lines[0].split(' '))[2]
            time = (lines[1].split('HEADERNAME '))[1]
            ret_msg = "messageGetTrue\n" + username + '\n' + time + '\n' + content
            
        if 'LIST' in requestline:
            ret_msg = "userlistTrue\n"
            userinfos = lines[3:len(lines)-2]
            ret_msg += '\n'.join(userinfos)
        #print ret_msg
        return ret_msg

class ClientFactoryForCs(object):
    def __init__(self, port):
        self.port = port
        self.protocol = ClientProtocolForCS()
        self.username = ''
        self.onlineUsers = []
        self.dialogs = []
        self.lastTalke = ''
    
    def sendHandshakeMsg(self):
        #print 'aaaaa'
        self.protocol.sendMessage("handshake") 
    
    def send_to_all(self, dialog):
        self.protocol.sendMessage("talkToAll",[self.username,dialog])
    
    def sendHeartbeatMsg(self):
        self.protocol.sendMessage("beat", self.username)
        #print 'Wait for server to response'
    
    def sendRequestOnlineUserMsg(self):
        self.protocol.sendMessage("requestOnlineUsers")
    
    def sendLeaveMsg(self):
        self.protocol.sendMessage("leave", self.username)
    
    def sendLoginMsg(self, username):
        print "self.port", self.port
        self.protocol.sendMessage("login", username)
    
    def keepAlive(self):
        sleep(10)
        while self.protocol.connected:
            self.sendHeartbeatMsg()
            sleep(10)
            #self.sendRequestOnlineUserMsg()
    #run the program at the very start
    #ensure the net is connected
    def startApplication(self):
        connect = False
        self.protocol.makeConnection()
        if self.protocol.connected:
            #print 'aaaaa'
            self.sendHandshakeMsg()
            msg = self.protocol.getMessage()
            if msg == "handshakeTrue":
                connect = True
        return connect
    
    def userLogin(self, username):
        self.username = username
        #print "Here is the ",username 
        print "self.port", self.port
        self.sendLoginMsg([username, self.port])
        #print "send!"
        msg = self.protocol.getMessage()
        #print "recieved! ", msg 
        ret_msg = False
        if msg == "loginTrue":
            print "login Successed!!!"
            ret_msg = True
        else:
            print "login failed!!!Change a name"
        return ret_msg
    
    def userGetDialogs(self):
        while self.protocol.connected:
            self.getMessage()
        
    def getMessage(self):
        recv = self.protocol.getMessage().split('\n')
        if recv[0] == "messageGetTrue":
            dialog = recv[2] + ' ' + recv[1] + '\n' + recv[3]
            print dialog
            self.dialogs.append(dialog)
            self.lastTalke = dialog
            return "talk"
        else:
            if recv[0] == "userlistTrue":
                self.updateUsers(recv)
                print self.getOnlineUsers()
            return "userlist"
    
    def getRecentDialog(self):
        return self.lastTalke
    
    def updateUsers(self, data):
        userinfos = data[1:]
        self.onlineUsers = userinfos
        
    def userTalking(self):
         while self.protocol.connected:
            msg = raw_input( self.username + '>')
            if msg != '':
                self.send_to_all(msg)
            else :
                print 'Empty msg, input again!'
            
    def userEnterTalkingRoom(self):
        #first thing when entring room, sleep and wakeup
        self.heartbeat = threading.Thread(target=self.keepAlive)
        self.heartbeat.start()
        #second request online userList
        self.sendRequestOnlineUserMsg()
        data = self.protocol.getMessage().split('\n')
        userinfos = []
        self.updateUsers(data)
        print self.onlineUsers
        #third thing is recieving the message
        # self.recving = threading.Thread(
        #     target=self.userGetDialogs)
        # #finally speak
        # self.talking = threading.Thread(
        #     target=self.userTalking)
        # self.recving.start()
        # self.talking.start()
        
    def getOnlineUsers(self):
        names = []
        for i in self.onlineUsers:
            name = i.split(' ')
            if self.username == name[0]:
                continue
            print i
            names.append(i)
        #print names
        return names
    
    def leaveApplication(self):
        self.sendLeaveMsg()
        self.protocol.lostConnection()
        self.protocol.connected = False
        print 'Lost connection!'
        #thread.exit_thread()
        

# def main():
#     port = random.randint(40000, 50000)
#     cli = ClientFactoryForCs(port)
#     connect = cli.startApplication()
#     print connect 
#     if connect:
#         username = raw_input('any username you want>')
#         if cli.userLogin(username):
#             cli.userEnterTalkingRoom()

# if __name__ == '__main__':
#     main()
