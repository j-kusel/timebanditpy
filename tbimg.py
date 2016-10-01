from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from scipy import integrate
import time

dpi = [60]
bpi = [4]
rows = 1
timelimits = [0, 0]
papersize = [11, 17]
paperxy = [0, 0]
margins = [10, 0]
opacity = [250]
insts = []
bars = []
grid = 0
#pixels = 0
globaloffset = 0

def setdpi(dots=60):
    dpi[0] = dots
    setpaper()

def setbpi(beatdiv=4): #????????????
    bpi[0] = beatdiv

def setrows(rownum=1):
    rows = rownum

def setmargins(x=10, y=0):
    margins[0]=x
    margins[1]=y

def setpaper(ps='11x17'):
    del papersize[:]
    del paperxy[:]
    for i in [int(x) for x in ps.split('x')]:
        papersize.append(i)
        paperxy.append(i*dpi[0])
    paperxy.reverse()

def plot():
    grid = paperinit()
    timelimits = imagesetup()
    tfont = ImageFont.truetype("FreeMono.ttf", 20)
    pixels = grid.load()
    txt = ImageDraw.Draw(grid)
    scalar = float(paperxy[0]-(margins[0]*2))/float(timelimits[1]-timelimits[0])
    icount = 0
    for m in insts:
        ys = int(float(icount)/float(len(insts))*paperxy[1])
        ye = int(float(icount+1)/float(len(insts))*paperxy[1])
        for n in m:
            txt.text((int(n.ylines[0].xloc*scalar)+12,ys+18), n.txt, (0,0,0), font=tfont)
            for i in n.ylines:
                for j in range(ys, ye):
                    pixels[int(float((i.xloc-timelimits[0])*scalar))+margins[0], j] = (i.opac, i.opac, i.opac)
        icount += 1
    grid.save('testimg.png')
    print 'yay'

def paperinit(sheet='11x17'): #return an image of blank paper
    setpaper(sheet)
    
    print paperxy
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
    del opacity[:]
    opacity.append(op)

def addinst(bars):
    """list of bars containing name, equation, timesig, offset"""
    insts.append([]) #add list of bars
    for b in bars:
        insts[-1].append(Bar(b))
    #print insts[name].key()
    
def drawbar(thebar, yoff):
    pass
    
class Bar:
    def __init__(self, measure):
        """
        takes a Measure object from timebandit.py
        """
        self.eq = measure.eq
        self.timesig = measure.timesig
        self.offset = measure.offset
        self.breadth = [0, paperxy[0]]
        self.tall = paperxy[1]
        self.ylines = []
        self.txt = str("(%d>%d)/%.2f" % (start, end, self.timesig))
        self.packbar()

    def packbar(self):
        for j in range(0, int(self.timesig)):
            m = int(integrate.quad(self.eq,0,float(j))[0]) + self.offset
            self.ylines.append(Line(m)) #dark lines
            for k in range(1, bpi[0]):
                n = int(integrate.quad(self.eq,0,float(j)+(float(k)/bpi[0]))[0]) + self.offset
                print opacity[0]
                self.ylines.append(Line(n,opacity[0])) #subdiv line loc, global opacity[0]
        self.ylines.append(Line(int(integrate.quad(self.eq,0,float(self.timesig))[0]) + self.offset, 100))
        self.breadth[0], self.breadth[1] = self.ylines[0].xloc, self.ylines[-1].xloc
        
class Line:
    def __init__(self, where, op=0):
        self.xloc = where
        self.opac = op
