#!/usr/bin/env python
import socket
import threading
import thread
from time import ctime, sleep
from format import Message
import sys

SERVER_HOST = ''
SERVER_PORT = 55455
ADDR = (SERVER_HOST, SERVER_PORT)
BUFSIZ = 2048

class ServerForCs(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.port = SERVER_PORT
        self.host = SERVER_HOST
        self.users = set()
        self.userinfos = {}
        self.sockets = set()
        self.msg = Message()
        self.running = 1
        self.lock = threading.Lock()
        self.threads = {}

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        s.bind(ADDR)
        s.listen(1)
        
        while self.running == True:
            clientsock, addr = s.accept()
            self.sockets.add(clientsock)
            print "accept msf from ", addr
            #when recieve a socket create a new thread
            t = threading.Thread(target=self.recv, args=[clientsock])
            #add beat thread for each clientsocket here
            #t2 = threading.Thread(target=self.recvBeat, args=[clientsock])
            self.threads[clientsock] = t
            #self.handshaked[clientsock] = [False,t2]
            
            #t2.start()
            t.start()
            #t2.start()
    
    def sendMessageToAClient(self, clientsock, types, data= None):
        msg = ''
        if types == "handshake":
            msg = self.msg.handshakeMsg(self.host)
        
        if types == "loginJudge":
            status = data[0]
            reason = data[1]
            msg = self.msg.loginServerMsg(status, reason)
        
        if types == "onlineUserList":
            msg = self.msg.getOnlineUserListMsg(data)
            print 'Send for heartbeat response'
        
        if types == "dialogReturn":
            username = data[0]
            dialog = data[1]
            msg = self.msg.serverSendToUserMsg(username, dialog)
        
        if msg != '':
            clientsock.send(msg)
        #Thread.exit_thread()
        
    def checkAliveUsers(self, client_host, client_port):
        pass
    
    def sendMessageToAllClient(self, username, msg):
        print self.threads
        for clientsock in self.threads.keys():
            self.sendMessageToAClient(clientsock, "dialogReturn", [username, msg])
        thread.exit_thread()
    
    def removeAliveClient(self, clientsock):
        client_host, client_port = clientsock.getpeername()
        if self.threads.has_key(clientsock):
            self.lock.acquire()
            del self.threads[clientsock]
            username = self.userinfos[(client_host, client_port)]
            self.users.remove(username)
            del self.userinfos[(client_host, client_port)]
            self.lock.release()
    
    def recvHandshake(self, clientsock):
        print 'Here'
        self.sendMessageToAClient(clientsock, "handshake")
        thread.exit_thread()
    
    def recvLogin(self, clientsock, lines):
        print 'LOGIN DEAL'
        client_host, client_port = clientsock.getpeername()
        requestline = lines[0].split(' ')
        username = requestline[2]
        port = (lines[1].split(' '))[1]
        name_exsit = False
        status = '1'
        reason = 'success'
        if username in self.users:
            name_exsit = True
        else:
            self.lock.acquire()
            self.users.add(username)
            self.userinfos[(client_host, client_port)] = username
            self.lock.release()
        
        if name_exsit == True:
            status = '0'
            reason = 'username already exist'
        print status, reason
        self.sendMessageToAClient(clientsock, "loginJudge", [status, reason])
        thread.exit_thread()
    
    def recvGetlist(self, clientsock):
        userinfos = {}
        userinfos = {}
        for ips in self.userinfos.keys():
            user = self.userinfos[ips]
            userinfos[user] = ips
        self.sendMessageToAClient(clientsock, "onlineUserList",userinfos) 
        thread.exit_thread()
    
    def recvLeave(self, clientsock):
        pass
    
    def recvMessage(self, clientsock, lines):
        #lines = clientsock.recv(BUFSIZ).split('\n')
        requestline = lines[0].split(' ')
        msg = lines[3]
        print msg
        username = requestline[2]
        #time = (lines[1].split('HEADERNAME '))[1]
        self.sendMessageToAllClient(username, msg)
        thread.exit_thread()
    
    def recvBeat(self, clientsock):
        #first time then send return message for getting the list
        client_host, client_port = clientsock.getpeername()
        userinfos = {}
        for ips in self.userinfos.keys():
            user = self.userinfos[ips]
            userinfos[user] = ips
        self.sendMessageToAClient(clientsock, "onlineUserList", userinfos)
        thread.exit_thread()
            #self.checkAliveUsers(client_host, client_port)userinfos = {}

    def recv(self, clientsock):
        while True:
            client_host, client_port = clientsock.getpeername()
            msg = clientsock.recv(BUFSIZ)
            lines = msg.split('\n')
            requestline = lines[0].split(' ')
            if msg != '':
                print 'Received message from ', client_host, client_port
                #judge type
                if 'MINET' in requestline:
                    print 'GOT HANDSHAKE'
                    t = threading.Thread(target=self.recvHandshake, args=[clientsock])
                    t.start()
                if 'LOGIN' in requestline:
                    t = threading.Thread(target=self.recvLogin, args=[clientsock, lines])
                    t.start()
                if 'GETLIST' in requestline:
                    t = threading.Thread(target=self.recvGetlist, args=[clientsock])
                    t.start()
                if 'BEAT' in requestline:
                    t = threading.Thread(target=self.recvBeat, args=[clientsock])
                    t.start()
                if 'MESSAGE' in requestline:
                    t = threading.Thread(target=self.recvMessage, args=[clientsock, lines])
                    t.start()
                if 'LEAVE' in requestline:
                    t = threading.Thread(target=self.recvLeave, args=[clientsock])
                    t.start()
                    thread.exit_thread()
            else:
                print 'No useful information recieved'

    def kill(self):
        self.running = 0

def main():
    server = ServerForCs()
    server.start()

if __name__ == "__main__":
    main()
    