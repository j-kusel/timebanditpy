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
        theeqs = []
        tbimg.setopacity(int(self.opslider.get()/100*255))
        tbimg.setbpi(int(self.bpislider.get()))
        tbimg.setrows(len(self.meas))
        for j in self.meas:
            tbimg.addbars(j.eq, j.timesig, j.beats[0])
        tbimg.plot()
        self.imgpop.destroy()

    def Align_popup(self):
        self.alignpop = Toplevel()
        tbTk.Build_align(self, self.alignpop)

        

    def Final_align(self, mstri, slvi, mstrm, slvm, pmstr, pslv):
        mi = Instrument()
        si = Instrument()
        for i in self.inst:
            if i.name == mstri:
                mi = i
            if i.name == slvi:
                si = i
        slv = si.measures[slvm]
        mstr = mi.measures[mstrm]
        slv.Shift(int(integrate.quad(mstr.eq,0,pmstr)[0]),
                  int(integrate.quad(slv.eq,0,pslv)[0]))
        slv.beatstr = slv.Beat_disp()
        self.alignpop.destroy()
        self.refresh()

    def Inst_manager(self):
        self.instpop = Toplevel()
        tbTk.Build_inst(self, self.instpop)
        

    def Save(self):
        tbFile.save(self.meas)

    def Load(self):
        measinsure = self.meas
        del self.meas[:]
        ld = tbFile.load()
        if (ld):
            app.bars.delete(0, END)
            for i in ld:
                print i
                self.meas.append(Measure(None, i[0],i[1],float(i[2]),i[3]))
        else:
            self.meas = measinsure

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
        self.beats = [
            o + self.offset for o in self.Calc(self.begin, self.end, self.timesig)
            ]
        app.bars.insert(END, self.beatstr)
        tbTk.Clear(app)

    def Shift(self, pivot, beat):
        print pivot
        print beat
        move = pivot-beat
        self.beats = [(int(x)+move) for x in self.beats]
        #self.offset = self.offset + move
        print self.beats
            

    def Calc(self, a, b, size):
        """returns collection of beat times when given start/end/length"""
        self.eq = lambda x: (60000/((b-a)/size*x+a))
        points = []
        names = ['0']
        points.append(0)
        for j in range(1, int(size)):
            points.append(int(integrate.quad(self.eq,0,j)[0]))
            names.append(str(points[-1]))
        self.beatstr = ' '.join(names)
        return points

    def Beat_disp(self):
        """returns beat info as string"""
        return ' '.join(str(x) for x in self.beats)

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
