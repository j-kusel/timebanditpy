from node import Node
#from timebandit.lib.tbLib import Instrument
import select
import Queue
import time
import threading

class Relay(threading.Thread):
    
    def __init__(self):
        self.router = {}
        self.nodes = {}
        self.status = 'standby'

        self._stopevent = threading.Event()
        self._sleepperiod = 1.0

        threading.Thread.__init__(self, name="timebandit")

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

    def run(self):
        self.inputs = [n.conn for n in self.nodes.values()]
        self.outputs = []
        self.status = 'online'
        
        while not self._stopevent.isSet() and self.inputs:
            time.sleep(0.05)
            readable, writable, exceptional = select.select(self.inputs, self.outputs, self.inputs)
            for conn in readable: # if node can be read,
                node = self.nodes[conn]
                data = conn.recv(1024) # read the node state message
                node.state = data
                if data == 'ready\x00':
                    print "ok it's ready"
                    node.state = data
                    #if conn not in self.outputs:
                    self.outputs.append(conn) # make 'ready' nodes available
                if data == 'error':
                    print 'remote error detected at node {}, attempting reconnect...'.format(node)
                    #node.connect()
                    if conn in self.outputs:
                        self.outputs.remove(conn)
                    self.inputs.remove(conn)
                    node.kill()


            for conn in writable:
                node = self.nodes[conn]
                try:
                    message = node.queue.get_nowait()
                    print 'sending %s to %s' % (message, node)
                    conn.send(message)

                except Queue.Empty:
                    # no messages waiting! stop checking if writable
                    # conn.send('standby')
                    #self.outputs.remove(conn)
                    # RESTORE THIS IF PROCESSING/READY MUTEX IMPLEMENTED
                    pass
                    
            for conn in exceptional:
                node = self.nodes[conn]
                print 'handling exceptional condition for', node
                # stop listening for input
                self.inputs.remove(conn)
                if conn in self.outputs:
                    self.outputs.remove(conn)
                # shut down thread here
                try:
                    node.retry()
                except:
                    print "retry failed, manually re-add node with the 'new' command"
                    node.kill()

        while (self.status == 'offline'):
            # wait for thread to join
            time.sleep(5)

    def cleanup(self):
        try:
            for node in self.nodes.values():
                node.kill()
        except:
            print 'error killing nodes'
        self.status = 'offline'
        self._stopevent.set()
        

def test():
    pass

if __name__ == '__main__':
    test()
