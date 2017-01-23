# eventually roll own sockets without having to use pdsend...
import socket
import os, sys
#from timebandit.lib.tbLib import InstManager, Measure

class Server(object):

    def __init__(self, sockets={'127.0.0.1': 0,}, port=7654):
        self.socket_list = sockets
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print 'socket successfully initialized'
        
    def bind(self, message='0', ip='localhost'):
        try:
            self.server.bind(('localhost', self.port))
            self.server.listen(10)

        except socket.error as msg:
            print 'bind failed - error {}:{}'.format(str(msg[0]), msg[1])
            sys.exit()

    def send(self, scheme=InstManager()):
        messages = []
        index = 0
        for inst in scheme:
            beats = ','.join([m.beats for m in scheme[inst]])
            messages.append("{}:{}~{}".format(index, inst, beats))
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

       


def main():

    HOST = 'localhost'
    PORT = 7464

    s = Server(port=PORT)
    s.bind()
    s.send(message='0:violin~4826,200,300,400,538;1:viola~728,462,3,534')


if __name__ == '__main__':
    main()

