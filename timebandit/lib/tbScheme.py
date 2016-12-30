from tbLib import InstManager, Measure, Rhythm
from scipy import integrate
import tbImg

class Scheme(object):
    def __init__(self):
        self.inst = InstManager()

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
                replica_meas.beatstr = replica_meas.Beat_disp()

        replica_meas.Shift(primary_meas.Eval(points[0])+primary_meas.offset, replica_meas.Eval(points[1]))
        #self.alignpop.destroy()
        #self.refresh()
#_#_#_#_#_#_#_#_#_#_!!!
    def pad(self, primary_meas=0, replica_meas=0, points=[]):
        pm = int(pmstr)
        ps = int(pslv)
        if pme=='' or pme=='end':
            termpt = mstr.timesig-1
        else:
            termpt = int(pme)
        ######
        slv.Shift(int(integrate.quad(primary_meas.eq,0,ppt)[0])+primary_meas.offset, int(integrate.quad(replica_meas.eq,0,rpt)[0]))
        # to prepare for aligntest.py code:
        tries = 100
        tolerance = 50

        eq_p = lambda x: (60000/((primary_meas.end-primary_meas.begin)/primary_meas.timesig*x+primary_meas.begin))
        f_p = integrate.quad(eq_m,primary_point,pme)[0]
        for i in range(0, tries):
            eq_r = lambda x: (60000/((replica_meas.end-replica_meas.begin)/replica_meas.timesig*x+replica_meas.begin))
            f_r = integrate.quad(eq_s,rpt,replica_meas.timesig-1)[0]
            dist = f_p - f_r
            print dist
            if abs(dist)<=tolerance:
                print "success! new timesig: %f, %d away" % (replica_meas.timesig,dist)
                break
            if dist>0:
                replica_meas.timesig+=.25
            else:
                replica_meas.timesig-=.25
            print "at try %d we are %d away" % (i, dist)

    def normalize(self, instrument=0, measure=0):
        """adjust offsets to shift timecodes relative to selected measure"""
        meas = self.inst[instrument][measure]
        off = meas.beats[0] - meas.offset
        for i in self.inst:
            for m in self.inst[i]:
                m.offset += off
