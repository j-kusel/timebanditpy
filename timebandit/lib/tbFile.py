from Tkinter import *
from tkFileDialog import *
from tbScheme import Scheme
from tbLib import Measure

def save(scheme=0):
    """write all measures to textfile, takes schema list as argument."""
    thefile = asksaveasfilename(defaultextension='.tb')
    if thefile is None:
        pass
    theinsts = scheme.inst
    pak = []
    schstr = []
    for i in theinsts:
        for j in theinsts[i]:
            del schstr[:]
            schstr.append(i)
            schstr.append(str(j.begin))
            schstr.append(str(j.end))
            schstr.append(str(j.timesig))
            schstr.append(str(j.offset))
            pak.append(' '.join(schstr))
    with open(thefile, 'w') as f:
        f.writelines([x+"\n" for x in pak])

def load(merge=0):
    """return 2d array of for measure initialization."""
    thefile = open(askopenfilename(), "r")
    finallines = []
    for l in thefile:
        fl = l.split(' ')
        if (len(fl) % 5 == 0):
            finallines.append([fl[0],int(fl[1]),int(fl[2]),float(fl[3]),int(fl[4])])
        else:
            print("ERROR: file corruption")
            return 0
    thefile.close()

    if merge==0:
        new_scheme = Scheme()
        for i in finallines:
            newmeas = Measure(i[0], i[1],i[2],i[3],i[4])
            new_scheme.inst[i[0]] += newmeas
        return new_scheme
    else:
        print 'merge feature not available yet'
        return 0
