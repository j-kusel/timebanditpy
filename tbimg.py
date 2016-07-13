from PIL import Image
from scipy import integrate
import time

dpi = 80
bpi = 4
rows = 1
timelimits = [0, 0]
paperxy = [1024, 768]
margins = [10, 0]
opacity = 150
insts = []
bars = []
grid = 0
pixels = 0
globaloffset = 0


def setdpi(dots=60):
    dpi = dots

def setbpi(beatdiv=4):
    bpi = beatdiv

def setrows(rownum=1):
    rows = rownum

def setmargins(x=10, y=0):
    margins[0]=x
    margins[1]=y

def plot():
    grid = papersetup()
    timelimits = imagesetup()
    pixels = grid.load()
    scalar = float(paperxy[0]-(margins[0]*2))/float(timelimits[1]-timelimits[0])
    print scalar
    #[ygrid.append(int(i/float(ylinessm[-1])*(paperxy[0]-1))) for i in ylines]
    #[ygridsm.append(int(i/float(ylinessm[-1])*(paperxy[0]-1))) for i in ylinessm]
    print paperxy[0], paperxy[1]
    icount = 0
    for m in insts:
        ys = int(float(icount)/float(len(insts))*paperxy[1])
        ye = int(float(icount+1)/float(len(insts))*paperxy[1])
        for n in m:
            print 'BAR', ys, ye
            for i in n.ylines:
                for j in range(ys, ye):
                    pixels[int(float((i.xloc-timelimits[0])*scalar))+margins[0], j] = (i.opac, i.opac, i.opac)
        icount += 1
    grid.save('testimg.png')
    print 'yay'

def papersetup(sheet='11x17'): #return an image of blank paper
    #paperxy = [int(x) for x in sheet.split('x')
    #paperxy.reverse()
    return Image.new('RGB', (paperxy[0],paperxy[1]), "white")
    
def imagesetup():
    lns = []
    for i in insts:
        for j in i:
            for k in j.ylines:
                lns.append(k.xloc)
    timelimits[0] = min(lns)
    timelimits[1] = max(lns)
    return timelimits

def reset():
    del insts[:]
    timelimits = [0,0]

def setopacity(op=0):
    opacity = op

def addinst(i):
    """list of bars containing name, equation, timesig, offset"""
    insts.append([]) #add list of bars
    for b in i:
        insts[-1].append(Bar(b[1],b[2],b[3]))
    #print insts[name].key()
    
def drawbar(thebar, yoff):
    pass
    
class Bar:
    def __init__(self, equation, beats, ofst):
        self.eq = equation
        self.timesig = beats
        self.offset = int(ofst)
        self.breadth = [0, paperxy[0]]
        self.tall = paperxy[1]
        self.ylines = []
        self.packbar()

    def packbar(self):
        for j in range(0, int(self.timesig)):
            m = int(integrate.quad(self.eq,0,float(j))[0]) + self.offset
            self.ylines.append(Line(m)) #dark lines
            for k in range(1, bpi):
                n = int(integrate.quad(self.eq,0,float(j)+(float(k)/bpi))[0]) + self.offset
                self.ylines.append(Line(n,opacity)) #subdiv line loc, global opacity
        self.ylines.append(Line(int(integrate.quad(self.eq,0,float(self.timesig))[0]) + self.offset, 100))
        self.breadth[0], self.breadth[1] = self.ylines[0].xloc, self.ylines[-1].xloc
        
class Line:
    def __init__(self, where, op=0):
        self.xloc = where
        self.opac = op
