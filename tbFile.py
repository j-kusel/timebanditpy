from Tkinter import *
from tkFileDialog import *


def save(theinsts):
    """write all measures to textfile, takes schema list as argument."""
    thefile = asksaveasfilename(defaultextension='.tb')
    if thefile is None:
        pass
    pak = []
    schstr = []
    for i in theinsts:
        for j in i.measures:
            del schstr[:]
            schstr.append(i.name)
            schstr.append(str(j.begin))
            schstr.append(str(j.end))
            schstr.append(str(j.timesig))
            schstr.append(str(j.offset))
            pak.append(' '.join(schstr))
    with open(thefile, 'w') as f:
        f.writelines([x+"\n" for x in pak])

def load():
    """return 2d array of for measure initialization."""
    thefile = open(askopenfilename(), "r")
    lines = thefile.readlines()
    thefile.close()
    finallines = []
    for l in lines:
        fl = l.split(' ')
        if (len(fl) % 5 == 0):
            finallines.append([fl[0],int(fl[1]),int(fl[2]),float(fl[3]),int(fl[4])])
        else:
            print("ERROR: file corruption")
            return 0
    return finallines
        
