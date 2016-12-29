from tbLib import InstManager, Measure, Rhythm
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

        f_p = integrate.quad(eq_primary,0,pts[0])[0]+primary_meas.offset
        f_s = integrate.quad(eq_secondary,0,pts[3])[0]+secondary_meas.offset
        final = 0
        for i in range(0, tries):
            eq_r = lambda x: (60000/((replica_meas.end-replica_meas.begin)/replica_meas.timesig*x+replica_meas.begin))
            f_r = integrate.quad(eq_r,pts[1],pts[2])[0]
            dist = abs(abs(f_p)-abs(f_s)) - abs(f_r)
            print "master lengths: %d %d // slave length: %d" % (f_p, f_s, f_r)
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
                eq_r = lambda x: (60000/((replica_meas.end-replica_meas.begin)/replica_meas.timesig*x+replica_meas.begin))
                f_r = integrate.quad(eq_r,pts[1],pts[3])[0]
                newdist = abs(abs(f_p)-abs(f_s)) - abs(f_r)
                if abs(newdist) > abs(dist):
                    replica_meas.end = ensure
                    replica_meas.begin = insure
                replica_meas.Calc()
                replica_meas.beatstr = replica_meas.Beat_disp()
                pass

        replica_meas.Shift(int(integrate.quad(primary_meas.eq,0,pts[0])[0])+primary_meas.offset, int(integrate.quad(secondary_meas.eq,0,pts[1])[0]))
        #self.alignpop.destroy()
        #self.refresh()

    def pad(self, p_meas, r_meas, ppt, rpt, pme):
        primary_meas = p_meas
        replica_meas = r_meas
###########################
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
        for i in self.scheme.inst:
            for m in i:
                m.offset += off
