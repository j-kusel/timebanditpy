# eventually roll own sockets without having to use pdsend...
#import socket
import os

class Server(object):

    def __init__(self, sockets={'localhost': 0,}, port=4500):
        self.socket_list = sockets
        self.port = port
        
    def send(self, ip, message):
        os.system("echo '{} {}' | pdsend {}".format(str(ip), str(message), str(self.port)))
