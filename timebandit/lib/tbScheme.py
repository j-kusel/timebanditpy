from tbLib import InstManager, Measure, Rhythm
from network.relay import Relay
from collections import OrderedDict
import threading
from scipy import integrate
import tbImg

class Scheme(object):
    def __init__(self):
        self.inst = InstManager()
        self.server = 0

    def create_inst(self, name='default'):
        """add a new instrument"""
        print "creating new instrument %s" % name
        self.inst[str(name)] = []
    
    def del_inst(self, name=''):
        """remove an instrument"""
        try:
            del self.inst[str(name)]
        except IndexError:
            print 'select an instrument to remove'
            pass

    def create(self, instrument='', start='', end='', time=''):
        """add measure to database from current input data"""
        try:
            measure_data = [instrument, int(start), int(end), float(time)]
            self.inst[measure_data[0]] += Measure(*measure_data)
        except TypeError:
            print "enter all necessary information for new measure"

    def generate_image(self, opacity=50, divisions=4):
        """plot image"""
        tbImg.reset()
        o = int(float(self.imgpop.opslider.get())/100*255)
        tbImg.setopacity(int(opacity/100*255))
        tbImg.setbpi(int(divisions))
        for i in self.inst:
            tbImg.addinst(self.inst[i])
        tbImg.plot()
        #self.imgpop.destroy()

    def align(self, primary_meas=0, replica_meas=0, primary_point=0.0, replica_point=0.0):
        """perform alignment calculations, close popup, refresh"""
        if primary_meas:
            replica_meas.Shift(primary_meas.Eval(primary_point)+primary_meas.offset,replica_meas.Eval(replica_point))
        else:
            replica_meas.Shift(primary_point,replica_meas.Eval(replica_point))
        #self.alignpop.destroy()

    def tweak(self, primary_meas=0, replica_meas=0, secondary_meas=0, points=[], direction=0):
        """primary meas, replica meas, primary pt, replica pt, secondary pt, replica movable pt"""
        x = int(integrate.quad(primary_meas.eq,0,points[0])[0])+primary_meas.offset
        y = int(integrate.quad(replica_meas.eq,0,points[1])[0])
        replica_meas.Shift(x, y)

        tries = 100
        tolerance = 50

        f_p = integrate.quad(primary_meas.eq,0,points[0])[0]+primary_meas.offset
        f_s = integrate.quad(secondary_meas.eq,0,points[3])[0]+secondary_meas.offset
        final = 0

        for i in range(0, tries):
            replica_meas.Calc()
            f_r = integrate.quad(replica_meas.eq,points[1],points[2])[0]
            dist = abs(abs(f_p)-abs(f_s)) - abs(f_r)
            print "master lengths: %d %d // slave length: %d" % (f_p, f_s, f_r)
            if (abs(dist)<=tolerance):
                final = 1
                print "%d <= %d tolerance" % (abs(dist), tolerance)
            else:
                print "not there yet %d" % dist
            insure = replica_meas
            if dist > 0:
                if direction==3: #both
                    replica_meas.begin-=0.5
                    replica_meas.end-=0.5
                elif direction==1: #change begin
                    replica_meas.begin-=1
                elif direction==2: #change end
                    replica_meas.end-=1
                else:
                    print "you gotta move something!"
                    break
            else:
                if direction==3: #both
                    replica_meas.begin+=0.5
                    replica_meas.end+=0.5
                elif direction==1: #change begin
                    replica_meas.begin+=1
                elif direction==2: #change end
                    replica_meas.end+=1
                else:
                    print "you gotta move something!"
                    break
            if final==1:
                replica_meas.Calc()
                f_r = integrate.quad(replica_meas.eq,points[1],points[3])[0]
                newdist = abs(abs(f_p)-abs(f_s)) - abs(f_r)
                if abs(newdist) > abs(dist):
                    replica_meas = insure
                replica_meas.Calc()

        replica_meas.Shift(primary_meas.Eval(points[0])+primary_meas.offset, replica_meas.Eval(points[1]))
        #self.alignpop.destroy()
        #self.refresh()

    def pad(self, primary_meas=0, replica_meas=0, points=[]):
        replica_meas.Shift(int(integrate.quad(primary_meas.eq,0,points[0])[0])+primary_meas.offset, 0)
        tries = 100
        tolerance = 50
        final = 0

        f_p = primary_meas.Eval(points[1], start=points[0])
        replica_meas.Calc()
        f_r = replica_meas.Eval(replica_meas.timesig)
        dist = abs(f_p) - abs(f_r)
        for i in range(0, tries):
            insure = replica_meas
            dist_test = dist
            dist = abs(f_p) - abs(f_r)
            print dist
            if final == 1:
                if abs(dist_test) > abs(dist):
                    replica_meas = insure
                    replica_meas.Calc()
                    break
            if abs(dist)<=tolerance:
                final = 1
                dist_test = dist
            if dist>0:
                replica_meas.timesig+=.25
            else:
                replica_meas.timesig-=.25
            replica_meas.Calc()
            f_r = replica_meas.Eval(replica_meas.timesig)
            print "at try %d we are %d away" % (i, dist)
        print "success! new timesig: %f, %d away" % (replica_meas.timesig,dist)
           

    def normalize(self, instrument=0, measure=0):
        """adjust offsets to shift timecodes relative to selected measure"""
        meas = self.inst[instrument][measure]
        off = meas.beats[0] - meas.offset
        for i in self.inst:
            for m in self.inst[i]:
                m.offset += off

    def start_server(self, ports=OrderedDict(), channels=OrderedDict()):
        print "ports: ", ports, "channels: ", channels
        if self.server:
            print "disconnect old server before starting a new one"
        elif ports and self.inst:
            self.server = Relay()
            n = 0
            used = []
            for inst in ports:
                for p in ports[inst]:
                    print "p=", p
                    if p in used:
                        print "adding {} to address {}:{}".format(inst, 'localhost', p)
                        self.server.add(inst=inst, IP='localhost', PORT=p)
                    else:
                        print "binding {} to address {}:{}".format(inst, 'localhost', p)
                        self.server.new(inst=inst, IP='localhost', PORT=ports[inst][0])
                        used.append(p)


                print self.server.router, self.server.nodes
                index = 0

            for i in self.inst:
                inst = self.inst[i]
                beats = []
                for m in inst:
                    beats.extend([m.beats[b] - m.beats[b-1] for b in range(1, len(m.beats))])
                print "BEETS: ", beats
                #################
                for c in channels[i]:
                    comm = "inst {} {}".format(c, " ".join([str(b) for b in beats]))
                    self.server.command(inst=i, msg=comm)

            self.server.start()

    def end_server(self):
        self.server.end()
        self.server.join()
        self.server = 0

    def network_command(self, msg):
        for inst in self.server.router:
            self.server.command(inst=inst, msg=msg)

    def network_transport(self, location):
        for inst in self.server.router:
            self.server.command(inst=inst, msg='transport {}'.format(location))

 
