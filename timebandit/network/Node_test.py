import socket
from Queue import Queue
from time import sleep
from ssl import wrap_socket
from timebandit.lib.tbLib import Instrument

class Node(socket.socket, Queue):

    def __init__(self, IP='localhost', PORT=7464):
        super(Node, self).__init__()
        Queue.__init__(self)
        self.IP = IP
        self.PORT = PORT
        self.addr = 0
        self.log = ["hello world",]
        self.state = 'empty'
        #self.setblocking(0)

        self.bind((self.IP, self.PORT))
        self.listen(10)
        print 'waiting on connection...'
        found = 0
        while not found:
            try:
                _, addr = self.accept() # refresh as a returned connection
                print 'external found at {}'.format(addr)
                self.addr = addr
                self.state = 'available'
                self.recv = _.recv
                self.send = _.send
                self.close = _.close
                found = 1
            except socket.error as msg:
                print 'external bind failure - error {}:{}'.format(str(msg[0]), msg[1])

    def __str__(self):
        return socket.__str__(socket)

    def transmit(self):
        try:      
            self.put(self.recv(1024))
                err = self.send(self.queue[-1])
            except socket.error:
                print 'connection failure - error {}'.format(str(err))

    def 
                

n = Node()
n.online()

