from tbLib import InstManager, Measure, Rhythm
import tbImg

class Scheme(object):
    def __init__(self):
        self.inst = InstManager()

    def create_inst(self, name='default'):
        """add a new instrument"""
        self.inst[str(name)] = []
    
    def del_inst(self, name=''):
        """remove an instrument"""
        try:
            del self.inst[str(name)]
        except IndexError:
            break

    def create(self, instrument='', start='', end='', time=''):
        """add measure to database from current input data"""
        measure_data = [instrument, start, end, time]
        if '' not in measure_data:
            self.inst[self.inst.index(measure_data[0])] += Measure(*measure_data)

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

    def align(self, primary_meas=0, replica_meas=0, primary_beat=0.0, replica_beat=0.0):
        """perform alignment calculations, close popup, refresh"""
        if primary_meas:
            replica_meas.Shift(primary_meas.Eval(primary_beat)+primary_meas.offset,replica_meas.Eval(replica_beat))
        else:
            replica_meas.Shift(primary_beat,replica_meas.Eval(replica_beat))
        #self.alignpop.destroy()

    def tweak(self, p_meas, r_meas, s_meas, pts, dir):
        """primary meas, replica meas, primary pt, replica pt, secondary pt, replica movable pt"""
        primary_meas = p_meas
        replica_meas = r_meas
        secondary_meas = s_meas

        replica_meas.Shift(int(integrate.quad(primary_meas.eq,0,pts[0])[0])+primary_meas.offset, int(integrate.quad(replica_meas.eq,0,pts[1])[0]))

        tries = 100
        tolerance = 50
        print "dir = %d" % (dir)

        eq_primary = lambda x: (60000/((primary_meas.end-primary_meas.begin)/primary_meas.timesig*x+primary_meas.begin))
        eq_secondary = lambda x: (60000/((secondary_meas.end-secondary_meas.begin)/secondary_meas.timesig*x+secondary_meas.begin))

    f_m = integrate.quad(eq_primary,0,pts[0])[0]+primary_meas.offset
        f_m2 = integrate.quad(eq_secondary,0,pts[3])[0]+secondary_meas.offset
        final = 0
        for i in range(0, tries):
            eq_s = lambda x: (60000/((replica_meas.end-replica_meas.begin)/replica_meas.timesig*x+replica_meas.begin))
            f_s = integrate.quad(eq_s,pts[1],pts[2])[0]
            dist = abs(abs(f_m)-abs(f_m2)) - abs(f_s)
            print "master lengths: %d %d // slave length: %d" % (f_m, f_m2, f_s)
            if (abs(dist)<=tolerance):
                final = 1
                print "%d <= %d tolerance" % (abs(dist), tolerance)
            insure = replica_meas.begin
            ensure = replica_meas.end
            if dist > 0:
                if dir==3: #both
                    replica_meas.begin-=0.5
                    replica_meas.end-=0.5
                elif dir==1: #change begin
                    replica_meas.begin-=1
                elif dir==2: #change end
                    replica_meas.end-=1
                else:
                    print "you gotta move something!"
            else:
                if dir==3: #both
                    replica_meas.begin+=0.5
                    replica_meas.end+=0.5
                elif dir==1: #change begin
                    replica_meas.begin+=1
                elif dir==2: #change end
                    replica_meas.end+=1
                else:
                    print "you gotta move something!"
            if final==1:
                eq_s = lambda x: (60000/((replica_meas.end-replica_meas.begin)/replica_meas.timesig*x+replica_meas.begin))
                f_s = integrate.quad(eq_s,pts[1],pts[3])[0]
                newdist = abs(abs(f_m)-abs(f_m2)) - abs(f_s)
                if abs(newdist) > abs(dist):
                    replica_meas.end = ensure
                    replica_meas.begin = insure
                replica_meas.Calc()
                replica_meas.beatstr = replica_meas.Beat_disp()
                break

        replica_meas.Shift(int(integrate.quad(primary_meas.eq,0,pts[0])[0])+primary_meas.offset, int(integrate.quad(secondary_meas.eq,0,pts[1])[0]))
        #self.alignpop.destroy()
        #self.refresh()

    def Final_pad(self, mstrm, slvm, pmstr, pslv, pme):
        for i in self.inst:
            if i == mstri:
                mi = self.inst[i]
            if i == slvi:
                si = self.inst[i]
        slv = si[slvm]
        mstr = mi[mstrm]
        pm = int(pmstr)
        ps = int(pslv)
        if pme=='' or pme=='end':
            termpt = mstr.timesig-1
        else:
            termpt = int(pme)
        ######
        slv.Shift(int(integrate.quad(primary_meas.eq,0,primary_point)[0])+primary_meas.offset, int(integrate.quad(replica_meas.eq,0,replica_point)[0]))
        # to prepare for aligntest.py code:
        master = [mstr.begin, mstr.end, mstr.timesig, pm]
        slave = [slv.begin, slv.end, slv.timesig, ps]
        tries = 100
        tolerance = 50

        eq_m = lambda x: (60000/((primary_meas.end-primary_meas.begin)/primary_meas.timesig*x+primary_measure.begin))
        f_m = integrate.quad(eq_m,primary_point,pme)[0]
        for i in range(0, tries):
            eq_s = lambda x: (60000/((replica_meas.end-replica_meas.begin)/replica_meas.timesig*x+replica_meas.begin))
            f_s = integrate.quad(eq_s,replica_point,replica_meas.timesig-1)[0]
            dist = f_m - f_s
            print dist
            if abs(dist)<=tolerance:
                print "success! new timesig: %f, %d away" % (replica_meas.timesig,dist)
                break
            if dist>0:
                replica_meas.timesig+=.25
            else:
                replica_meas.timesig-=.25
            print "at try %d we are %d away" % (i, dist)
