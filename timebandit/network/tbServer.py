# eventually roll own sockets without having to use pdsend...
import socket, select, thread
import os, sys, time
import Queue
#from timebandit.lib.tbScheme import Scheme

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

    def send_pd(self, scheme):#=Scheme()):
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

def clientthread(conn):
    conn.send('hey cool ur connected lol')
    while True:

        data = conn.recv(1024)
        reply = 'OK...' + data
        if not data:
            break

        conn.sendall(reply)
    conn.close()

def link():
    s = Server(port=7464)
    s.server.setblocking(0)
    try:
        s.server.bind(('localhost', s.port))
        s.server.listen(10)

    except socket.error as msg:
        print 'bind failed - error {}:{}'.format(str(msg[0]), msg[1])
        sys.exit()

    inputs = [s.server]
    outputs = []
    message_queues = {}
    instances = []

    while inputs:
        readable, writable, exceptional = select.select(inputs, outputs, inputs)

        for sock in readable:
            if sock is s.server:
                conn, addr = s.server.accept()
                print 'connected with {}:{}'.format(addr[0], addr[1])
                conn.setblocking(0)
                inputs.append(conn)

                message_queues[conn] = Queue.Queue()

            else:
                data = sock.recv(1024)
                if data:
                    print 'received %s from %s' % (data, sock.getpeername())
                    message_queues[sock].put(data)
                    if sock not in outputs:
                        outputs.append(sock)
                else:
                    # no data == closed connection!
                    print 'closing', addr, 'after reading no data'
                    if sock in outputs:
                        outputs.remove(sock)
                    inputs.remove(sock)
                    sock.close()

                    # remove message queue
                    del message_queues[sock]

        for sock in writable:
            try:
                next_msg = message_queues[sock].get_nowait()
            except Queue.Empty:
                # no messages waiting! stop checking if writable
                print 'output queue for', sock.getpeername(), 'is empty'
                outputs.remove(sock)
            else:
                print 'sending %s to %s' % (next_msg, sock.getpeername())
                sock.send(next_msg)

        for sock in exceptional:
            print 'handling exceptional condition for', sock.getpeername()
            # stop listening for input
            inputs.remove(sock)
            if sock in outputs:
                outputs.remove(sock)
            sock.close()

            del message_queues[sock]

    # s.server.close()

    #try:
    #    conn, addr = s.server.accept()
    #    print 'connected with {}:{}'.format(addr[0], addr[1])
    
    #    conn.send('0:violin~1200,750,1500,800;1:viola~300,450,2400,150;2:cello~834,257,1930,764;3:bass~200,300,245,120')
    #    time.sleep(20)
    #finally:
    #    conn.close()

def test():
    s = Server(port=7464)
    s.server.setblocking(0)
    try:
        s.server.bind(('localhost', s.port))
        s.server.listen(10)

    except socket.error as msg:
        print 'bind failed - error {}:{}'.format(str(msg[0]), msg[1])
        sys.exit()



if __name__ == '__main__':
    link()
