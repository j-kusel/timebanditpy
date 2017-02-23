import argparse, os, sys, traceback
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from scipy import integrate
from Tkinter import *
from tkFileDialog import *
from lib import tbImg, tbFile, tbTk
from lib.tbScheme import Scheme
from network.tbServer import Server
from collections import OrderedDict
from PIL import Image, ImageTk

class Application(Frame):

    def __init__(self, master):
        Frame.__init__(self, master)
        self.grid()
        tbTk.Build_core(self, master)
        
        self.scheme = Scheme()

    def New(self):
        """clear all"""
        self.bars.delete(0, END)
        self.inst = InstManager()
        tbTk.refresh(self)

    def scheme_dispatcher(self, command, **kwargs):
        try:
            getattr(self.scheme, command)(**kwargs)
            tbTk.refresh(self)
        except:
            traceback.print_exc()

    def Inst_manager(self):
        self.instpop = Toplevel()
        tbTk.Build_inst(self, self.instpop)

    def Save(self):
        tbFile.save(self.scheme)

    def Load(self, merge=0):
        new_scheme = tbFile.load()
        if new_scheme:
            self.scheme = new_scheme
            self.insts.delete(0, END)
            self.bars.delete(0, END)
            tbTk.refresh(self)
        else:
            print "error: file load failed"

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

