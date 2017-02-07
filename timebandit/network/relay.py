from node import Node
#from timebandit.lib.tbLib import Instrument
import select
import Queue
import time

class Relay(object):
    
    def __init__(self):
        self.router = {}
        self.nodes = {}

    def new(self, inst=0, IP='localhost', PORT=7464):
        """add a fresh Instrument to the Server - takes Instrument, IP, PORT"""
        addr = (IP, PORT)
        #if assert isinstance(inst, Instrument):
        n = Node(IP=IP, PORT=PORT)
        self.nodes[n.conn] = n
        if inst:
            self.router[inst] = [self.nodes[n.conn]]
        #else:
        #    print "Relay nodes dict must take timebandit Instrument as a key"

    def add(self, inst=0, IP='localhost', PORT=7464):
        addr = (IP, PORT)
        if addr in [n.getpeername() for n in self.nodes]:
            self.router[inst].append(self.nodes[addr])
        else:
            print "use new method to initialize a new Node"

    def command(self, inst=0, msg='null'):
        for n in self.router[inst]:
            n.queue.put(msg)
            print n.queue

    def monitor(self):
        inputs = [n.conn for n in self.nodes.values()]
        outputs = []
        print inputs

        while inputs:
            readable, writable, exceptional = select.select(inputs, outputs, inputs)
            print 'loop top: ', readable, writable
            for conn in readable: # if node can be read,
                print 'readable start'
                node = self.nodes[conn]
                data = conn.recv(1024) # read the node state message
                print 'read successful'
                if data:
                    print 'received %s from %s' % (data, node)
                    node.state = data
                    if data == 'ready':# and conn not in outputs:
                        outputs.append(conn) # make 'ready' nodes available
                        print 'append to outputs successful'
                    elif data == 'error':
                        print 'remote error detected at node {}, attempting reconnect...'.format(node)
                        node.connect()
                    else:
                        print node.state
                        outputs.remove(conn)
                        inputs.remove(conn)
                        node.kill()
            print 'loop middle: ', readable, writable
            for conn in writable:
                node = self.nodes[conn]
                print 'do we even enter the writable loop?'
                try:
                    message = node.queue.get_nowait()
                    print 'sending %s to %s' % (message, node)
                    conn.send(message)

                except Queue.Empty:
                    # no messages waiting! stop checking if writable
                    print 'output queue for', node, 'is empty'
                    conn.send('standby')
                    outputs.remove(conn)
                    
            for conn in exceptional:
                node = self.nodes[conn]
                print 'handling exceptional condition for', node
                # stop listening for input
                inputs.remove(conn)
                if conn in outputs:
                    outputs.remove(conn)
                # shut down thread here
                try:
                    node.retry()
                except:
                    print "retry failed, manually re-add node with the 'new' command"
                    node.kill()

def test():
    r = Relay()
    r.new(inst='violaah', PORT=8100)
    r.new(inst='violiiiin', PORT=8101)
    r.command(inst='violaah', msg='hooray it works')
    time.sleep(5)
    r.command(inst='violiiiin', msg='OMG M-M-M-M-MONSTER KILL')
    r.monitor()

if __name__ == '__main__':
    test()
