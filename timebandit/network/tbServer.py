# eventually roll own sockets without having to use pdsend...
import socket
import os, sys
from timebandit.lib.tbScheme import Scheme

class Server(object):

    def __init__(self, sockets={'127.0.0.1': 0,}, port=7654):
        self.socket_list = sockets
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print 'socket successfully initialized'
        
    def bind_pd(self, message='0', ip='localhost'):
        try:
            self.server.bind(('localhost', self.port))
            self.server.listen(10)

        except socket.error as msg:
            print 'bind failed - error {}:{}'.format(str(msg[0]), msg[1])
            sys.exit()

    def send_pd(self, scheme=Scheme()):
        messages = []
        index = 0
        for i in scheme.inst:
            beats = ','.join([','.join([str(s) for s in m.beats]) for m in scheme.inst[i]])
            messages.append("{}:{}~{}".format(index, i, beats))
            index += 1
        packet = ';'.join(messages)
        print packet
        while(True):
            try:
                conn, addr = self.server.accept()
                print 'Connected with {}:{}'.format(addr[0], addr[1])
                conn.send(packet)
            finally:
                conn.close()
