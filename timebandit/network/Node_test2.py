from socket import socket
from Queue import Queue
from time import sleep
from ssl import wrap_socket

class Node(Queue):

    def __init__(self, IP='localhost', PORT=7464):
        self.IP = IP
        self.PORT = PORT
        self.log = ["hello world",]
        self.setblocking(0)


        self.bind((self.IP, self.PORT))
        self.listen(10)
        print 'waiting on connection...'


        self.test = self.accept()[0] # refresh as a returned connection           

        #self.put('HOLY SHIT')
        #self.send(self.queue[-1])        
        Queue.__init__(self)


    def online(self):
        while True:
            sleep(1)
            #try:
            #self.recv(1024)
            self.send('oh hey there')
            #except self.error:

n = Node()
n.online()

