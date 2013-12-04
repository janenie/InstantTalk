#!usr/bin/env python

import socket
import threading
import select
import time
import random

def main():

    class Chat_Server(threading.Thread):
        def __init__(self, port):
            threading.Thread.__init__(self)
            self.running = 1
            self.conn = None
            self.addr = None
            self.port = port

        def run(self):
            HOST = ''
            PORT = self.port
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST,PORT))
            s.listen(1)

            while self.running == True:
                clientsock, addr = s.accept()
                t = threading.Thread(target=self.recv, args=[clientsock])
                t.start()

        def recv(self, clientsock):
            while True: # Assume always alive
                msg = clientsock.recv(1024)
                if msg != '':
                    print 'Received: ', msg

        def kill(self):
            self.running = 0
     
    class Chat_Client(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.running = 1
            self.connected_peers = {}

        def run(self):
            while self.running == 1:
                cmd = raw_input("cmd>")
                if cmd == 'connect':
                    host, port, name = raw_input("host, port, name>").split()
                    self.connect(host, int(port), name)
                elif cmd == 'send':
                    msg = raw_input("msg>")
                    name = raw_input("name>")
                    self.send(msg, name)
                elif cmd == 'exit':
                    self.kill()

        def send(self, msg, name):
            sock = self.connected_peers[name]
            sock.send(msg)
            
        def connect(self, host, port, name):
            # create a new socket and connect to dest
            # use name to identify the sock, name is for debug purpose
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.connect((host, port))
            self.connected_peers[name] = sock
            
        def kill(self):
            self.running = 0

    port = random.randint(10000, 60000)
    print "Port:", port
    chat_server = Chat_Server(port)
    chat_client = Chat_Client()
    chat_server.start()
    chat_client.start()

if __name__ == "__main__":
    main()
