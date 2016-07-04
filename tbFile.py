from Tkinter import *
from tkFileDialog import *


def save(themeasures):
    """write all measures to textfile, takes schema list as argument."""
    thefile = asksaveasfilename(defaultextension='.txt')
    if thefile is None:
        pass
    pak = []
    schstr = []
    for i in themeasures:
        del schstr[:]
        schstr.append(str(i.begin))
        schstr.append(str(i.end))
        schstr.append(str(i.timesig))
        schstr.append(str(i.offset))
        pak.append(' '.join(schstr))
    with open(thefile, 'w') as f:
        f.writelines([x+"\n" for x in pak])

def load():
    """return 2d array of for measure initialization."""
    thefile = open(askopenfilename(), "r")
    lines = thefile.readlines()
    finallines = []
    for l in lines:
        floatlines = [int(float(x)) for x in l.split(' ')]
        finallines.append(floatlines)
    thefile.close()
    if (len(finallines) % 4 == 0):
        return finallines
    else:
        print("ERROR: file corruption")
        return 0
