#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Base Server
 
import socket
import sys
import thread
import threading
import time


host = ''
port = 51423
portForMessage = 51424
#clientArray = [] #存放在线用户

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
s.bind((host, port))
s.listen(100)

s2 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s2.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
s2.bind((host, portForMessage))
print "Waiting for connections... "
s2.listen(100)
global eve
eve = threading.Event()

global cancelSignal
mutex = threading.Lock()
mutex.acquire()
cancelSignal = 1000
mutex.release()
global usernames
usernames = set()
global userips
userips = set()
global login
login = {}
global count
count = 0
def sendMessageToAll(clientsock2,client2,count): #群聊监听用户发来信息
    while True:
        eve.clear()   # 若已设置标志则清除
        eve.wait()    # 调用wait方法
        global cancelSignal
        if cancelSignal != 1000:
            if count == cancelSignal:
                time.sleep(0.01)
                mutex.acquire()
                cancelSignal = 1000
                mutex.release()
                eve.clear()
                clientsock2.send("close")
                clientsock2.close()
                thread.exit_thread()
                pass
            pass
        print messageAll
        clientsock2.send(messageAll)
        time.sleep(0.05)
        pass

def createClient(clientsock,client,count,name):

    while True:
        reco = clientsock.recv(1024)
        rec = reco.split('^^^')
        if rec[0] == 'message': #群聊监听用户发来信息
            global messageAll
            messageAll = rec[1]
            eve.set()
            pass
        if rec[0] == 'ClientNumber':
            clientsock.send(str(count))
            pass
        if rec[0] == 'AllName':
            namestr = ''
            for key in usernames:
                namestr += key
                namestr += '^^^'
            clientsock.send(namestr)
            pass
        if rec[0] == 'positionIp':
            clientsock.send(login[name])
            pass
        if rec[0] == 'positionPort':
            f = open('clientInformation.txt')
            m = ''
            for x in xrange(100):
                line = f.readline()
                if str(x) == rec[1]:
                    m = line.split(' ')
                    break
                    pass
                pass
            clientsock.send(m[2])
            pass
        if rec[0] == 'close':
           
            usernames.remove(name)
            userips.remove(login[name])
            del login[name]
            #mutex.release()
            #终结该用户的群聊线程
            global cancelSignal
            mutex.acquire()
            cancelSignal = count
            mutex.release()
            clientsock.close()
            eve.set()
            break
            pass
        pass
    thread.exit_thread()
    pass

while True: #主线程，用来监听client的连接
    
    clientsock, client = s.accept()
    name = clientsock.recv(1024)
    #jud = name in usernames
    if name in usernames:
        clientsock.send("False^^^username")
        print "False^^^username"
        continue
        pass
    else:
        if client[0] in userips:
            clientsock.send("False^^^username")
            print "False^^^username"
            continue
            pass
        else:
            clientsock.send("True^^^username")
            usernames.add(name)
            userips.add(client[0])
            login[name] = client[0]
            print "True^^^username"
    clientsock2, client2 = s2.accept()
    #记录当前用户的个数，通过数文档下用户的个数
    mutex.acquire()
    count += 1
    mutex.release()
    
    thread.start_new_thread(createClient, (clientsock,client,count,name))
    thread.start_new_thread(sendMessageToAll, (clientsock2,client2,count))
    pass