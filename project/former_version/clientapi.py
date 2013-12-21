#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Base client
# 建立一个线程来接收群聊信息
import socket
import time

# client先写连接服务器接口再写群聊连接接口，如下：
# server = clientAPI.connectToServer(name)
# server2 = clientAPI.connectToServerForAllMessage()

def connectToServerForAllMessage(): #连接到服务器，socket用来做群聊
	s2 = socket.socket()
	s2.connect_ex(('localhost',51424))
	return s2 #返回连接后的socket
	pass

def connectToServer(name): #连接到服务器，参数为用户的名字
	s = socket.socket()
	s.connect_ex(('localhost',51423))
	s.send(name)
	return s #返回连接后的socket
	
	pass

def createP2pServer(): #创建一个两个人聊天的P2P连接，开始的时候放在一个线程里面监听
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
	s.bind(("", 51426))
	s.listen(100)
	clientsock, client = s.accept()
	return clientsock
	pass

def getClientNumber(s): #获取所有用户的个数，第一个参数是socket
	s.send('ClientNumber^^^ClientNumber')
	AllclientName = s.recv(1024)
	return AllclientName
	pass

def getAllClientName(s): #获取用户的名字，第一个参数是socket，第二个是用户是第几个登陆的
	s.send("AllName^^^AllName")
	clientName = s.recv(10000)
	allName = clientName.split('^^^')
	return allName
	pass

def getClientIp(s,name): #获取用户的IP地址，第一个参数是socket，第二个是用户是第几个登陆的
	s.send('positionIp^^^' + name)
	clientIp = s.recv(128)
	return clientIp
	pass


def TalkToSomeOne(s,name):
	s2 = socket.socket()
	ipadd = getClientIp(s,name)
	s2.connect_ex((ipadd,51426))
	return s2
	pass

def sendAllMessage(s2,str): #向所有的用户发送信息，第一个参数是socket，第二个是信息
	s2.send('message^^^' + str)
	pass

def close(s): #关闭客户端，参数为socket
	s.send('close^^^close')
	s.close()
	pass

