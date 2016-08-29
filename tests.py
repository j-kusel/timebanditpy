from scipy import integrate
import send2pd as pd
import tbimg
import tbFile
import tbTk
from PIL import Image, ImageTk

class Instrument:

    def __init__(self, name='<<null>>'):
        self.name = str(name)
        self.measures = []
        if self.name != '<<null>>':
            app.insts.insert(END, self.name)
            
class Measure:

    def __init__(self, whichinst, s, e, ts, off=0):
        self.begin = s
        self.end = e
        self.timesig = ts
        self.offset = off
        self.rhys = []
        self.beatstr = ''
        self.beats = self.Calc(self.begin, self.end, self.timesig)
        
    def Shift(self, pivot, beat): #started reworking how offset works
        print pivot
        print beat
        self.offset = pivot - beat
        print self.offset, "here's the offset"
        print self.beats, "here's the beats"
        self.beatstr = self.Beat_disp()
        
    def Calc(self, a, b, size):
        """returns collection of beat times when given start/end/length"""
        self.eq = lambda x: (60000/((b-a)/size*x+a))
        points = []
        names = [str(self.offset)]
        points.append(0)
        for j in range(1, int(size)):
            points.append(integrate.quad(self.eq,0,j)[0])
            names.append(str(points[-1]+self.offset))
        self.beatstr = ' '.join(names)
        return points

    def Beat_disp(self):
        """returns beat info as string"""
        return ' '.join(str(x+self.offset) for x in self.beats)

    def Add_rhy(self):
        self.rhys.append(Rhythm(self))

class Rhythm:

    def __init__(self, parent): #initialize with tie to Measure
        self.peq = parent.eq
        self.transients = []

    def Add_tr(self, note):
        self.transients.append(int(integrate.quad(self.peq,0,note)))
        self.Update_tr()

    def Del_tr(self, which):
        pass

    def Update_tr(self):
        pass

def three_anchor_tempo(master_m, slave_m):

    tolerance = 12
    tries = 500
    f_m = integrate.quad(master_m.eq,0,master_m.timesig-1)[0]
    for i in range(0, tries):
        f_s = integrate.quad(slave_m.eq,0,slave_m.timesig-1)[0]
        f_dist = f_m - f_s
        print abs(f_dist)
        if (abs(f_dist)<=tolerance):
            break
        print f_dist 
        if f_dist > 0:
            slave_m.end-=(float(i)/tries)
        else:
            slave_m.end+=(float(i)/tries)
        slave_m.Calc(slave_m.begin, slave_m.end, slave_m.timesig-1)
    return slave_m.end

demo1 = Measure('Null', 20, 150, 7)
demo2 = Measure('Null', 220, 54, 8)

print demo1.beats
print demo2.beats 

demo1.end = int(three_anchor_tempo(demo1, demo2))
print demo2.end
print demo1.Calc(demo1.begin, demo1.end, demo1.timesig)
print demo1.beats
print demo2.beats
