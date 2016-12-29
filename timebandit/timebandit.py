import argparse, os, sys, traceback
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from scipy import integrate
from Tkinter import *
from tkFileDialog import *
from lib import tbImg, tbFile, tbTk
from lib.tbScheme import Scheme
from collections import OrderedDict
from PIL import Image, ImageTk

class Application(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)
        self.grid()
        tbTk.Build_core(self, master)
        
        self.scheme = Scheme()
        self.server = ''

    def New(self):
        """clear all"""
        self.bars.delete(0, END)
        tbTk.Clear(self)
        self.inst = InstManager()

    def scheme_dispatcher(self, command, **kwargs):
        try:
            getattr(self.scheme, command)(**kwargs)
            self.refresh()
        except:
            traceback.print_exc()
        self.refresh()

    def refresh(self):
        """rebuild instruments list, beat strings"""
        self.insts.delete(0, END)
        for i in self.scheme.inst:
            self.insts.insert(END, i)
            for m in self.scheme.inst[i]:
                m.beatstr = m.Beat_disp()
        self.bars.delete(0,END)

    def Build_server(self):
        """open a socket to remote pure data clients"""
        from network.server import Server
        self.server = Server()
        self.server.send(message='test')

    def pdplay(self):
        if self.server:      
            for i in self.scheme.inst:
                part = ' '.join([j.beatstr for j in self.scheme.inst[i]])
                self.server.send(message=part)

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


    def get_sel_inst(self):
        """find what's selected"""
        return self.inst[self.inst.index(int(self.insts.curselection()[0]))]

    def Display_measures(self):
        """show measures"""
        self.bars.delete(0, END)
        if len(self.scheme.inst) != 0:
            print self.insts.get(ACTIVE)
            for i in self.scheme.inst[self.insts.get(ACTIVE)]:
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

