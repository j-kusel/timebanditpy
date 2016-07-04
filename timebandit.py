from scipy import integrate
from Tkinter import *
from tkFileDialog import *
import send2pd as pd
import tbimg
import tbFile
from PIL import Image, ImageTk

class Application(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)
        self.grid()

        self.stlab = Label(self, text='start')
        self.stlab.grid(row=0, column=0, sticky=E)
        self.st = Entry(self)
        self.st.grid(row = 0, column = 1, sticky = W)
        self.endlab = Label(self, text='end')
        self.endlab.grid(row=1,column=0, sticky=E)
        self.end = Entry(self)
        self.end.grid(row = 1, column = 1, sticky = W)
        self.longlab = Label(self, text='beats')
        self.longlab.grid(row=2, column=0, sticky=E)
        self.long = Entry(self)
        self.long.grid(row=2, column=1, sticky=W)

        self.rhy = Entry(self)
        self.rhy.grid(row = 0, column = 2, columnspan=2)

        self.go = Button(self, text="go", command=self.create, padx = 96)
        self.go.grid(row=3, column=0, columnspan=2)
        self.eval = Button(self, text="eval...", command=self.rhyeval)
        self.eval.grid(row = 1, column = 2)

        self.result = StringVar()
        self.output = Label(master, textvariable=self.result, relief=RAISED)
        self.output.grid(row = 1, column = 0)

        self.therhy = StringVar()
        self.rhylab = Label(master, textvariable=self.therhy, relief=RAISED)
        self.rhylab.grid(row = 1, column = 3)

        self.bars = Listbox(self)
        self.bars.grid(row = 4, column = 0, columnspan=2, ipadx=26)

        self.alignbut = Button(self, text='align...', command=self.Align_popup)
        self.alignbut.grid(row=1, column=3)

        self.playbut = Button(self, text='play!', command=self.pdplay)
        self.playbut.grid(row=2, column=2)

        self.printbut = Button(self, text='print...', command=self.imgeval)
        self.printbut.grid(row=2, column=3)

        self.savebut = Button(self, text='save...', command=self.Save)
        self.savebut.grid(row=3, column=3)
        self.loadbut = Button(self, text='load...', command=self.Load)
        self.loadbut.grid(row=3, column=2)

        self.schema = []

    def create(self):
        st = self.st.get()
        e = self.end.get()
        l = self.long.get()
        print st, e, l
        if st != '' and e != '' and l != '':
            self.schema.append(Measure(int(st), int(e), float(l)))

    def refresh(self):
        self.bars.delete(0, END)
        for i in self.schema:
            self.bars.insert(END, i.beatstr) 

    def rhyeval(self):
        self.rhypop = Toplevel()
        self.rhypop.title("rhythm manager")
        self.rhyloc = schema[int(self.bars.curselection()[0])]
        self.rhyinfo = self.rhyinfograb(self.rhyloc)
        
        self.schinfo = Label(self.rhypop, textvariable=self.rhyloc)
        self.therhy.set(str(integrate.quad(self.schema[loc].eq,0,float(self.rhy.get()))[0]))

    def rhyinfograb(self, theloc):
        pass

    def pdplay(self):
        for i in range(len(self.schema)):
            print self.schema[i].beatstr
            pd.sendout(i, self.schema[i].beatstr)
        pd.sendout(99, 1)

    def imgeval(self):
        self.imgpop = Toplevel()
        self.imgpop.title("print")
        
        self.opslider = Scale(self.imgpop, from_=0, to=100)
        self.opslider.grid(row=0, column=0)
        self.bpislider = Scale(self.imgpop, from_=1, to=10)
        self.bpislider.grid(row=1, column=0)
        self.plot = Button(self.imgpop, text="print", command=self.imggen)
        self.plot.grid(row=0, column=1)

    def imggen(self):
        tbimg.reset()
        theeqs = []
        tbimg.setopacity(int(self.opslider.get()/100*255))
        tbimg.setbpi(int(self.bpislider.get()))
        tbimg.setrows(len(self.schema))
        for j in self.schema:
            tbimg.addbars(j.eq, j.timesig, j.beats[0])
        tbimg.plot()
        self.imgpop.destroy()

    def Align_popup(self):
        self.alignpop = Toplevel()
        self.alignpop.title("align")

        self.masteralign = Listbox(self.alignpop, exportselection=0)
        self.slavealign = Listbox(self.alignpop, exportselection=0)
        self.masteralign.grid(row=0, column=0)
        self.slavealign.grid(row=0, column=1)

        self.pivotmaster = Entry(self.alignpop)
        self.pivotslave = Entry(self.alignpop)
        self.pivotmaster.grid(row=1, column=0)
        self.pivotslave.grid(row=1, column=1)

        self.goalign = Button(self.alignpop, text='align!', command=self.Final_align)
        self.goalign.grid(row=1, column=2)

        for i in self.schema:
            self.masteralign.insert(END, i.beatstr)
            self.slavealign.insert(END, i.beatstr)

    def Final_align(self):
        mstr = self.schema[int(self.masteralign.curselection()[0])]
        slv = self.schema[int(self.slavealign.curselection()[0])]
        slv.Shift(int(integrate.quad(mstr.eq,0,float(self.pivotmaster.get()))[0]),
                  int(integrate.quad(slv.eq,0,float(self.pivotslave.get()))[0]))
        slv.beatstr = slv.Beat_disp()
        self.alignpop.destroy()
        self.refresh()

    def Save(self):
        tbFile.save(self.schema)

    def Load(self):
        schemainsure = self.schema
        del self.schema[:]
        ld = tbFile.load()
        if (ld):
            for i in ld:
                print i
                self.schema.append(Measure(i[0],i[1],float(i[2]),i[3]))
        else:
            self.schema = schemainsure
            
class Measure:

    def __init__(self, s, e, ts, off=0):
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
