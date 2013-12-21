#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Base client

import clientAPI
import thread
import threading
import time

def close(server):
	global getStr
	while True:
		mutex.acquire()
		getStr = raw_input('input')
		str = getStr
		mutex.release()
		if getStr == '1': #关闭客户端
			clientAPI.close(server)
			break
			pass
		if getStr == '2': #和某个人聊天
			s22 = clientAPI.TalkToSomeOne(server,'namee')
			print "s22TalkToSomeOne success"
			s22.send("connect")
			s22.recv(1024)
			break
			pass
		else:
			clientAPI.sendAllMessage(server, str)
	pass

def createOne(server):
	s11 = clientAPI.createP2pServer()
	print "s11create success"
	s11.recv(1024)
	s11.send("success")
	pass

name = 'namee'
server = clientAPI.connectToServer(name)
judg = server.recv(20)#接收是否有重复的姓名
if(judg != 'False^^^username'):
	server2 = clientAPI.connectToServerForAllMessage()

	time.sleep(0.02)
	ClientNumber = clientAPI.getClientNumber(server)
	print "clientNumber " + ClientNumber
	AllClientName = clientAPI.getAllClientName(server)
	for x in xrange(int(ClientNumber)):
		print AllClientName[x]
		pass
	global getStr
	mutex = threading.Lock()
	mutex.acquire()
	getStr = "0"
	mutex.release()


	thread.start_new_thread(close,(server,))
	thread.start_new_thread(createOne,(server,))
	while True:
		if getStr == '1':
			break
			pass
		print server2.recv(1024)
else:
	print "False^^^username"



