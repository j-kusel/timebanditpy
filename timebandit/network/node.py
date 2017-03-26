import socket
import Queue
from time import sleep
from ssl import wrap_socket
#from timebandit.lib.tbLib import Instrument

class Node(object):

    def __init__(self, IP='localhost', PORT=8100):
        self.IP = IP
        self.PORT = PORT
        self.addr = 0
        self.conn = 0
        self.queue = Queue.Queue()
        self.log = ["hello world",]
        self.state = 'empty'
        self.channels = 0
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            #self.server.setblocking(1)
            self.server.bind((self.IP, self.PORT))
            self.server.listen(10)
        except socket.error as msg:
            print 'node bind failure: error {}:{}'.format(str(msg[0]), msg[1])
        else:
            self.connect()

    def __str__(self):
        return "external at {} - status: {}".format(self.addr, self.state)

    def kill(self):
        try:
            if self.conn:
                self.conn.send('close')
                #self.conn.shutdown(socket.SHUT_RDWR)
                self.conn.setblocking(1)
                if self.conn.recv(1024) == 'safe':
                    sleep(0.2)
                    self.conn.close()
                    self.queue = Queue.Queue()
        except socket.error as msg:
            print 'node shutdown failure - error {}:{}'.format(str(msg[0]), msg[1])

    def connect(self):
        try:
            print 'connect a local or remote timebandit~ external'
            self.conn, self.addr = self.server.accept()
            print 'timebandit~ external found at: {}'.format(self.addr)
        except socket.error as msg:
            print 'timebandit~ connect failure - error {}:{}'.format(str(msg[0]), msg[1])
            if self.conn:
                self.kill()
            self.state = 'failed'
        finally:
            return self.state # 'ready' if successful, 'failed' if socket.error
