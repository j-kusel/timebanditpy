from PIL import Image
from scipy import integrate
import time

dpi = 80
bpi = 4
rows = 1
timemax = 0
timemin = 0
paperxy = [1024, 768]
opacity = 150
bars = []
grid = 0
pixels = 0


def setdpi(dots=60):
    dpi = dots

def setbpi(beatdiv=4):
    bpi = beatdiv

def setrows(rownum=1):
    rows = rownum

def plot():
    grid = papersetup()
    pixels = grid.load()
    themin = min([b.breadth[0] for b in bars])
    themax = max([b.breadth[1] for b in bars])
    scalar = float(paperxy[0]-10)/float(themax - themin)
    print scalar
    #[ygrid.append(int(i/float(ylinessm[-1])*(paperxy[0]-1))) for i in ylines]
    #[ygridsm.append(int(i/float(ylinessm[-1])*(paperxy[0]-1))) for i in ylinessm]
    print paperxy[0], paperxy[1]
    for h in range(0, len(bars)):
        a=0
        y1 = int(float(h)/float(len(bars))*paperxy[1])
        y2 = bars[h].tall
        print 'BAR', h, y1, y2
        for i in bars[h].ylines:
            for j in range(y1, y1+y2):
                #print y1, y2, float(i.xloc)*scalar, j
                pixels[int(float(i.xloc)*scalar), j] = (i.opac, i.opac, i.opac)
    grid.save('testimg.png')
    print 'yay'

def papersetup(sheet='11x17'): #return an image of blank paper
    #[paperxy.append(int(i)) for i in sheet.split('x')] #remember to dpi scale later
    #paperxy.reverse()
    return Image.new('RGB', (paperxy[0],paperxy[1]), "white")
    
def imagesetup():
    
    pass

def reset():
    bars[:] = []

def setopacity(op=0):
    opacity = op

def addbars(eq, beats, offset):
    bars.append(Bar(eq, beats, offset))
    for i in bars:
        i.tall = int(paperxy[1]/len(bars))

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
        self.breadth[0], self.breadth[1] = self.ylines[0].xloc, self.ylines[-1].xloc
        
class Line:
    def __init__(self, where, op=0):
        self.xloc = where
        self.opac = op
