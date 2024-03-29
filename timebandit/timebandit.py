import os, sys, argparse
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from scipy import integrate
from Tkinter import *
from tkFileDialog import *
import send2pd as pd
from lib import tbImg, tbFile, tbTk
from lib.tbLib import *
from collections import OrderedDict
from PIL import Image, ImageTk

class Application(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)
        self.grid()
        tbTk.Build_core(self, master)
        
        self.inst = InstManager()
        self.meas = []

    def create_inst(self, pop):
        """add a new instrument"""
        name = str(pop.iname.get())
        self.inst[name] = []
        pop.ilist.insert(END, name)
        self.refresh()

    def del_inst(self, popup, delind):
        """remove an instrument"""
        del self.inst[self.inst.index(delind)]
        popup.ilist.delete(delind)
        self.refresh()

    def create(self):
        """add measure to database from current input data"""
        measure_data = [int(self.insts.curselection()[0]), int(self.st.get()), int(self.end.get()), float(self.long.get())]
        if '' not in measure_data:
            self.inst[self.inst.index(measure_data[0])] += Measure(*measure_data)
        self.refresh()

    def refresh(self):
        """rebuild instruments list, beat strings"""
        self.insts.delete(0, END)
        for i in self.inst:
            self.insts.insert(END, i)
            for m in self.inst[i]:
                m.beatstr = m.Beat_disp()
        self.bars.delete(0,END)

    def pdplay(self):
        """send measure information to pure data"""
        for i in range(len(self.meas)):
            print self.meas[i].beatstr
            pd.sendout(i, self.meas[i].beatstr)
        pd.sendout(99, 1)

    def imgeval(self):
        """open image popup"""
        self.imgpop = Toplevel()
        tbTk.Build_img(self, self.imgpop) #main application, top window
        
    def imggen(self):
        """plot image"""
        tbImg.reset()
        o = int(float(self.imgpop.opslider.get())/100*255)
        tbImg.setopacity(o)
        tbImg.setbpi(int(self.imgpop.bpislider.get()))
        for i in self.inst:
            tbImg.addinst(self.inst[i])
        tbImg.plot()
        self.imgpop.destroy()

    def Align_popup(self):
        """build the alignment window"""
        self.alignpop = Toplevel()
        tbTk.Build_align(self, self.alignpop)


    def Final_align(self, mm, sm, mp, sp):
        """perform alignment calculations, close popup, refresh"""
        if mm:
            sm.Shift(mm.Eval(mp)+mm.offset,sm.Eval(sp))
        else:
            sm.Shift(mp,sm.Eval(sp))
        self.alignpop.destroy()
        self.refresh()

    def Final_tweak(self, mm, sm, mm2, pts, dir):
        """master inst, slave inst, master meas, slave meas, master pt, slave pt, master movable pt, slave movable pt"""
        #### next step: tighten up tolerance!!
        slv = sm
        mstr = mm
        mstr2 = mm2
                   
        slv.Shift(int(integrate.quad(mstr.eq,0,pts[0])[0])+mstr.offset,
                  int(integrate.quad(slv.eq,0,pts[1])[0]))

        tries = 100
        tolerance = 50
        print "dir = %d" % (dir)

        eq_m = lambda x: (60000/((mstr.end-mstr.begin)/mstr.timesig*x+mstr.begin))
        eq_m2 = lambda x: (60000/((mstr2.end-mstr2.begin)/mstr2.timesig*x+mstr2.begin))

        f_m = integrate.quad(eq_m,0,pts[0])[0]+mstr.offset
        f_m2 = integrate.quad(eq_m2,0,pts[3])[0]+mstr2.offset
        final = 0
        for i in range(0, tries):
            eq_s = lambda x: (60000/((slv.end-slv.begin)/slv.timesig*x+slv.begin))
            f_s = integrate.quad(eq_s,pts[1],pts[2])[0]
            dist = abs(abs(f_m)-abs(f_m2)) - abs(f_s)
            print "master lengths: %d %d // slave length: %d" % (f_m, f_m2, f_s)
            if (abs(dist)<=tolerance):
                final = 1
                print "%d <= %d tolerance" % (abs(dist), tolerance)
            insure = slv.begin
            ensure = slv.end        
            if dist > 0:
                if dir==3: #both
                    slv.begin-=0.5
                    slv.end-=0.5
                elif dir==1: #change begin
                    slv.begin-=1
                elif dir==2: #change end
                    slv.end-=1
                else:
                    print "you gotta move something!"
            else:
                if dir==3: #both
                    slv.begin+=0.5
                    slv.end+=0.5
                elif dir==1: #change begin
                    slv.begin+=1
                elif dir==2: #change end
                    slv.end+=1
                else:
                    print "you gotta move something!"
            if final==1:
                eq_s = lambda x: (60000/((slv.end-slv.begin)/slv.timesig*x+slv.begin))
                f_s = integrate.quad(eq_s,pts[1],pts[3])[0]
                newdist = abs(abs(f_m)-abs(f_m2)) - abs(f_s)
                if abs(newdist) > abs(dist):
                    slv.end = ensure
                    slv.begin = insure                
                slv.Calc()
                slv.beatstr = slv.Beat_disp()                
                break

        slv.Shift(int(integrate.quad(mstr.eq,0,pts[0])[0])+mstr.offset,
                  int(integrate.quad(slv.eq,0,pts[1])[0]))        
        self.alignpop.destroy()
        self.refresh()
    #############################

    def Final_pad(self, mstri, slvi, mstrm, slvm, pmstr, pslv, pme):
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
        slv.Shift(int(integrate.quad(mstr.eq,0,pm)[0])+mstr.offset,
                  int(integrate.quad(slv.eq,0,ps)[0]))
        # to prepare for aligntest.py code:
        master = [mstr.begin, mstr.end, mstr.timesig, pm]
        slave = [slv.begin, slv.end, slv.timesig, ps]
        tries = 100
        tolerance = 50
        
        eq_m = lambda x: (60000/((master[1]-master[0])/master[2]*x+master[0]))
        f_m = integrate.quad(eq_m,pm,termpt)[0]
        for i in range(0, tries):
            eq_s = lambda x: (60000/((slave[1]-slave[0])/slave[2]*x+slave[0]))
            f_s = integrate.quad(eq_s,ps,slave[2]-1)[0]
            dist = f_m - f_s
            print dist
            if abs(dist)<=tolerance:
                print "success! new timesig: %f, %d away" % (slave[2],dist)
                break
            if dist>0:
                slave[2]+=.25
            else:
                slave[2]-=.25
            print "at try %d we are %d away" % (i, dist)
        self.refresh()

    def Inst_manager(self):
        self.instpop = Toplevel()
        tbTk.Build_inst(self, self.instpop)

    def Save(self):
        tbFile.save(self.inst)

    def Load(self, merge=0):
        instinsure = self.inst
        ld = tbFile.load()
        if (ld):
            if merge==0:
                self.inst = InstManager()
                self.insts.delete(0, END)
                self.bars.delete(0, END)
            for i in ld:
                print 'ld=', i
                newmeas = Measure(i[0], i[1],i[2],float(i[3]),i[4])
                self.inst[i[0]] += newmeas
        else:
            self.inst = instinsure
        self.refresh()

    def Merge(self): 
        ## good candidate for a decorator?!
        self.Load(merge=1)

    def Norm(self):
        """adjust offsets so there are no negative timecodes"""
        ## REFACTOR THIS
        o = self.inst[self.inst.index(int(self.insts.curselection()[0]))][int(self.bars.curselection()[0])]
        off = o.beats[0] - o.offset
        for i in self.inst:
            for m in self.inst[i]:
                m.offset += off
        self.refresh()

    def New(self):
        """clear all"""
        self.bars.delete(0, END)
        tbTk.Clear(self)
        self.meas = InstManager()

    def get_sel_inst(self):
        """find what's selected"""
        return self.inst[self.inst.index(int(self.insts.curselection()[0]))]

    def Display_measures(self, sel):
        """show measures"""
        self.bars.delete(0, END)
        if len(self.inst) != 0:
            for i in self.get_sel_inst():
                self.bars.insert(END, i)

# TESTING
def testsuite():
    inst = []
    for i in range(0,3):
        inst.append(Instrument(name=str(i)))
        for i in range(0,3):
            inst[-1].measures.append(Measure(inst[-1],60,120,5))

    for i in inst:
        print i

# MAIN
def main():    
    root = Tk()
    root.title("timebandit")
    #root.geometry("1024x768")

    app = Application(root)
    root.mainloop()    

def package_entry():
    if len(sys.argv) == 1:
        print 'noargs'
        main()
    elif sys.argv[1] == 'test':
        print "tests not available in this release"
        #testsuite()
    else:
        try:
            import lib.tbUtil as tbUtil
            parser = tbUtil.tbParser(sys.argv)
            command, flags = parser.parse()
            tbUtil.AppExec(command, flags)
        except ImportError:
            raise ImportError("tbParser import failed!")
            
if __name__ == "__main__":
    main()

