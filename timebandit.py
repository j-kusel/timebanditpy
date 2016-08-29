from scipy import integrate
from Tkinter import *
from tkFileDialog import *
import send2pd as pd
import tbimg
import tbFile
import tbTk
from PIL import Image, ImageTk

class Application(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)
        self.grid()
        tbTk.Build_core(self, master)
        
        self.inst = []
        self.meas = []

    def create_inst(self, pop):
        name = str(pop.iname.get())
        self.inst.append(Instrument(name))
        pop.ilist.insert(END, name)
        self.refresh()

    def del_inst(self, popup, delind):
        self.inst.pop(delind)
        popup.ilist.delete(delind)
        self.refresh()

    def create(self):
        st = self.st.get()
        e = self.end.get()
        l = self.long.get()
        ins = int(self.insts.curselection()[0])
        print st, e, l
        if st != '' and e != '' and l != '':
            self.get_sel_inst().append(Measure(ins, int(st), int(e), float(l)))

    def refresh(self):
        self.insts.delete(0, END)
        for i in self.inst:
            self.insts.insert(END, i.name)
            for j in i.measures:
                j.beatstr = j.Beat_disp()
        self.bars.delete(0,END)

    def rhyeval(self):
        self.rhypop = Toplevel()
        self.rhypop.title("rhythm manager")
        self.rhyloc = self.meas[int(self.bars.curselection()[0])]
        self.rhyinfo = self.rhyinfograb(self.rhyloc)
        
        self.schinfo = Label(self.rhypop, textvariable=self.rhyloc)
        self.therhy.set(str(integrate.quad(self.rhyloc.eq,0,float(self.rhy.get()))[0]))

    def rhyinfograb(self, theloc):
        pass

    def pdplay(self):
        for i in range(len(self.meas)):
            print self.meas[i].beatstr
            pd.sendout(i, self.meas[i].beatstr)
        pd.sendout(99, 1)

    def imgeval(self):
        self.imgpop = Toplevel()
        tbTk.Build_img(self, self.imgpop) #main application, top window
        
    def imggen(self):
        tbimg.reset()
        o = int(float(self.imgpop.opslider.get())/100*255)
        tbimg.setopacity(o)
        tbimg.setbpi(int(self.imgpop.bpislider.get()))
        for i in self.inst:
            thebars = []
            for j in i.measures:
                thebars.append([i.name, j.eq, j.timesig, j.offset, j.begin, j.end])
            tbimg.addinst(thebars)
        tbimg.plot()
        self.imgpop.destroy()

    def Align_popup(self):
        self.alignpop = Toplevel()
        tbTk.Build_align(self, self.alignpop)

    def Final_align(self, mstri, slvi, mstrm, slvm, pmstr, pslv):
        print mstri, slvi, mstrm, slvm, pmstr, pslv
        pm = 0
        ps = 0
        mi = Instrument()
        si = Instrument()
        for i in self.inst:
            if i.name == mstri:
                mi = i
            if i.name == slvi:
                si = i
        slv = si.measures[slvm]
        mstr = mi.measures[mstrm]
        if pmstr.lower() == 'end':
            pm = mstr.timesig
        elif pmstr.lower() == 'start':
            pm = 0
        else:
            pm = int(pmstr)-1
        if pslv.lower() == 'end':
            ps = slv.timesig
        elif pslv.lower() == 'start':
            ps = 0
        else:
            ps = int(pslv)-1
        slv.Shift(int(integrate.quad(mstr.eq,0,pm)[0])+mstr.offset,
                  int(integrate.quad(slv.eq,0,ps)[0]))
        self.alignpop.destroy()
        self.refresh()

    def Inst_manager(self):
        self.instpop = Toplevel()
        tbTk.Build_inst(self, self.instpop)

    def Save(self):
        tbFile.save(self.inst)

    def Load(self):
        instinsure = self.inst
        del self.inst[:]
        ld = tbFile.load()
        if (ld):
            app.insts.delete(0, END)
            app.bars.delete(0, END)
            for i in ld:
                if not (i[0] in [x.name for x in self.inst]):
                    self.inst.append(Instrument(i[0]))
                self.inst[-1].measures.append(Measure(i[0], i[1],i[2],float(i[3]),i[4]))
        else:
            self.inst = instinsure
        self.refresh()

    def Norm(self):
        o = self.inst[int(self.insts.curselection()[0])].measures[int(self.bars.curselection()[0])]
        off = o.beats[0] - o.offset
        print off
        for i in self.inst:
            for j in i.measures:
                j.offset += off
                print j.offset
        self.refresh()

    def New(self):
        self.bars.delete(0, END)
        tbTk.Clear(self)
        del self.meas[:]

    def get_sel_inst(self):
        return self.inst[int(self.insts.curselection()[0])].measures

    def Display_measures(self, sel):
        self.bars.delete(0, END)
        if len(self.inst) != 0:
            for i in self.get_sel_inst():
                app.bars.insert(END, i.beatstr)

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
        app.bars.insert(END, self.beatstr)
        tbTk.Clear(app)

    def Shift(self, pivot, beat): #started reworking how offset works
        print pivot
        print beat
        self.offset = pivot - beat
        print self.offset, "here's the offset"
        print self.beats, "here's the beats"
        self.beatstr = self.Beat_disp()
        app.refresh()

    def Calc(self, a, b, size):
        """returns collection of beat times when given start/end/length"""
        self.eq = lambda x: (60000/((b-a)/size*x+a))
        points = []
        names = [str(self.offset)]
        points.append(0)
        for j in range(1, int(size)):
            points.append(int(integrate.quad(self.eq,0,j)[0]))
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

    
root = Tk()
root.title("timebandit")
#root.geometry("1024x768")

app = Application(root)
root.mainloop()
