from node import Node
from timebandit.lib.tbLib import Instrument

class Relay(object):
    
    def __init__(self):
        self.router = {}
        self.nodes = {}

    def new(self, inst=0, IP='localhost', PORT=7464):
        """add a fresh Instrument to the Server - takes Instrument, IP, PORT"""
        addr = (IP, PORT)
        if assert isinstance(inst, Instrument):
            self.nodes[addr] = Node(IP=IP, PORT=PORT)
            self.router[inst] = [self.nodes[addr]]
        else:
            print "Relay nodes dict must take timebandit Instrument as a key"

    def add(self, inst=0, IP='localhost', PORT=7464):
        addr = (IP, PORT)
        if addr in self.nodes:
            self.router[inst].append(self.nodes[addr])
        else:
            print "use new method to initialize a new Node"

    def command(self, inst=0, msg='null'):
        for n in self.router[inst]:
            n.put(msg)

    def 
    inputs = values(self.nodes)
    while inputs:
        readable, writable, exceptional = select.select(inputs, outputs, inputs)

        for node in readable:
            if sock is s.server:
                conn, addr = s.server.accept()
                print 'connected with {}:{}'.format(addr[0], addr[1])
                conn.setblocking(0)
                inputs.append(conn)

                message_queues[conn] = Queue.Queue()

            else:
                data = node.recv(1024)
                if data:
                    print 'received %s from %s' % (data, node.addr)#node.getpeername())
                    node.state = data
                    if node.state == 'ready'
                    if node not in outputs:
                        outputs.append(node)
                else:
                    # no data == closed connection!
                    print 'state unknown'
                    if sock in outputs:
                        outputs.remove(node)
                    inputs.remove(node)
                    sock.close()

                    # remove message queue
                    del message_queues[node]

        for node in writable:
            try:
                next_msg = node.get_nowait()
            except Queue.Empty:
                # no messages waiting! stop checking if writable
                print 'output queue for', node.addr, 'is empty'
                outputs.remove(node)
            else:
                print 'sending %s to %s' % (next_msg, node.addr)
                sock.send(next_msg)

        for sock in exceptional:
            print 'handling exceptional condition for', node.addr
            # stop listening for input
            inputs.remove(node)
            if node in outputs:
                outputs.remove(node)
            # shut down thread here
            node.close()

            del message_queues[sock]
