import os
import socket
import time

port = 3000

def changeport(newport):
    port = newport

def sendout(ind, mess):
    message = str(ind) + ' ' + str(mess) + ';'
    os.system("echo '" + message + "' | pdsend " + str(port))
