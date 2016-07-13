from Tkinter import *

invarm = None
invars = None

def Build_core(app, master):

    app.menubar = Menu(app)

    menu = Menu(app.menubar, tearoff=0)
    app.menubar.add_cascade(label='file', menu=menu)
    menu.add_command(label='new', command=app.New)
    menu.add_command(label='open...', command=app.Load)
    menu.add_command(label='merge...')
    menu.add_command(label='save...', command=app.Save)
    menu.add_command(label='print...', command=app.imgeval)

    menu = Menu(app.menubar, tearoff=0)
    app.menubar.add_cascade(label='edit', menu=menu)
    menu.add_command(label='add inst...', command=app.Inst_manager)
    menu.add_command(label='align...', command=app.Align_popup)
    menu.add_command(label='evaluate...', command=app.rhyeval)
    menu.add_command(label='preferences...')

    menu = Menu(app.menubar, tearoff=0)
    app.menubar.add_cascade(label='playback', menu=menu)
    menu.add_command(label='play!', command=app.pdplay)

    master.configure(menu=app.menubar)

    app.stlab = Label(app, text='start')
    app.stlab.grid(row=0, column=0, sticky=E)
    app.st = Entry(app)
    app.st.grid(row = 0, column = 1, sticky = W)
    app.endlab = Label(app, text='end')
    app.endlab.grid(row=1,column=0, sticky=E)
    app.end = Entry(app)
    app.end.grid(row = 1, column = 1, sticky = W)
    app.longlab = Label(app, text='beats')
    app.longlab.grid(row=2, column=0, sticky=E)
    app.long = Entry(app)
    app.long.grid(row=2, column=1, sticky=W)

    app.rhy = Entry(app)
    app.rhy.grid(row = 0, column = 2, columnspan=2)

    app.go = Button(app, text="go", command=app.create, padx = 96)
    app.go.grid(row=3, column=0, columnspan=2)
    app.eval = Button(app, text="eval...", command=app.rhyeval)
    app.eval.grid(row = 1, column = 2)

    app.result = StringVar()
    app.output = Label(app, textvariable=app.result, relief=RAISED)
    app.output.grid(row = 1, column = 0)

    app.therhy = StringVar()
    app.rhylab = Label(app, textvariable=app.therhy, relief=RAISED)
    app.rhylab.grid(row = 1, column = 3)

    app.bars = Listbox(app)
    app.bars.grid(row = 4, column = 0, columnspan=2, ipadx=26)

    app.insts = Listbox(app)
    app.insts.grid(row = 5, column = 0, columnspan=2, ipadx=26)
    app.insts.bind('<<ListboxSelect>>', app.Display_measures)

    app.alignbut = Button(app, text='align...', command=app.Align_popup)
    app.alignbut.grid(row=1, column=3)

    app.playbut = Button(app, text='play!', command=app.pdplay)
    app.playbut.grid(row=2, column=2)

    app.printbut = Button(app, text='print...', command=app.imgeval)
    app.printbut.grid(row=2, column=3)

    app.savebut = Button(app, text='save...', command=app.Save)
    app.savebut.grid(row=3, column=3)
    app.loadbut = Button(app, text='load...', command=app.Load)
    app.loadbut.grid(row=3, column=2)    

def Build_img(app, pop):
    """Takes main application, Toplevel() window as arguments"""
    pop.title("print")
        
    pop.opslider = Scale(pop, from_=0, to=100)
    pop.opslider.grid(row=0, column=0)
    pop.oplab = Label(pop, text='opacity')
    pop.oplab.grid(row=0, column=1)
    
    pop.bpislider = Scale(pop, from_=1, to=10)
    pop.bpislider.grid(row=1, column=0)
    pop.bpilab = Label(pop, text='subdivisions')
    pop.bpilab.grid(row=1, column=1)

    pop.imgex = Button(pop, text='cancel', command=pop.destroy)
    pop.imgex.grid(row=2, column=0)
    pop.plot = Button(pop, text="print", command=app.imggen)
    pop.plot.grid(row=2, column=1)

def Build_align(app, pop):
    """Takes main application, Toplevel() window as arguments"""
    
    pop.title("align")
    menuinst = []
    for i in app.inst:
        menuinst.append(i.name)
    invarm = StringVar()
    invars = StringVar()
    invarm.set(menuinst[0])
    invars.set(menuinst[0])

    pop.masteralign = Listbox(pop, exportselection=0)
    pop.masterdrop = OptionMenu(pop, invarm, *(menuinst),
                                command = (lambda invarm: al_box_update(app, pop.masteralign, invarm)))
    pop.masterdrop.grid(row = 0, column=0)
    pop.slavealign = Listbox(pop, exportselection=0)
    pop.slavedrop = OptionMenu(pop, invars, *(menuinst),
                                command = (lambda invars: al_box_update(app, pop.slavealign, invars)))
    pop.slavedrop.grid(row=0, column=1)
    pop.masteralign.grid(row=1, column=0)
    pop.slavealign.grid(row=1, column=1)

    for i in app.get_sel_inst():
        pop.masteralign.insert(END, i.beatstr)
        pop.slavealign.insert(END, i.beatstr)

    pop.pivotmaster = Entry(pop)
    pop.pivotslave = Entry(pop)
    pop.pivotmaster.grid(row=2, column=0)
    pop.pivotslave.grid(row=2, column=1)

    
    pop.goalign = Button(pop, text='align!', command= (lambda: al_final(app, pop)))
    pop.goalign.grid(row=1, column=2)

def al_box_update(app, box, whichinst):
    """takes app, Listbox to update, and instrument name as string"""
    box.delete(0, END)
    for i in app.inst:
        if i.name == whichinst:
            for j in i.measures:
                box.insert(END, j.beatstr)

def al_final(app, pop):
    app.Final_align(pop.masterdrop.cget("text"),
                    pop.slavedrop.cget("text"),
                    int(pop.masteralign.curselection()[0]),
                    int(pop.slavealign.curselection()[0]),
                    pop.pivotmaster.get(), #str
                    pop.pivotslave.get()) #str

def Build_inst(app, pop):
    """Takes main application, Toplevel() window as arguments"""
    pop.title("instrument manager")

    pop.ilab = Label(pop, text='instrument name', relief=RAISED)
    pop.ilab.grid(row=0, column=0)
    pop.iname = Entry(pop)
    pop.iname.grid(row=0, column=1)
    pop.igo = Button(pop, text='add instrument',
                     command=(lambda: app.create_inst(pop)))
    pop.igo.grid(row=0, column=2)
    pop.ilist = Listbox(pop, exportselection=0)
    pop.ilist.grid(row=1, column=0, columnspan=2)
    for i in app.inst:
        pop.ilist.insert(END, i.name)
    pop.idel = Button(pop, text='delete instrument',
                      command=(lambda: app.del_inst(pop, int(pop.ilist.curselection()[0]))))
    pop.idel.grid(row=2, column=1)
    

def Clear(app):
    """clears entry boxes after file change or function call"""
    app.st.delete(0, END)
    app.end.delete(0, END)
    app.long.delete(0, END)
    app.rhy.delete(0, END)


        
