from Tkinter import *

invarm = None
invars = None

def Build_core(app, master):

    app.menubar = Menu(app)

    menu = Menu(app.menubar, tearoff=0)
    app.menubar.add_cascade(label='file', menu=menu)
    menu.add_command(label='new', command=app.New)
    menu.add_command(label='open...', command=app.Load)
    menu.add_command(label='merge...', command=app.Merge)
    menu.add_command(label='save...', command=app.Save)
    menu.add_command(label='print...', command=(lambda: Build_img(app)))

    menu = Menu(app.menubar, tearoff=0)
    app.menubar.add_cascade(label='edit', menu=menu)
    menu.add_command(label='add inst...', command=(lambda: self.Build_inst(app)))
    menu.add_command(label='align...', command=(lambda: self.Build_align(app)))
    #menu.add_command(label='evaluate...', command=app.rhyeval)
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

    app.go = Button(app, text="go", command=create_final, padx = 96)
    app.go.grid(row=3, column=0, columnspan=2)
    #app.eval = Button(app, text="eval...", command=app.rhyeval)
    #app.eval.grid(row = 1, column = 2)

    app.result = StringVar()
    app.output = Label(app, textvariable=app.result, relief=RAISED)
    app.output.grid(row = 1, column = 0)

    app.therhy = StringVar()
    app.rhylab = Label(app, textvariable=app.therhy, relief=RAISED)
    app.rhylab.grid(row = 1, column = 3)

    app.bars = Listbox(app, exportselection=0)
    app.bars.grid(row = 4, column = 0, columnspan=2, ipadx=26)

    app.insts = Listbox(app, exportselection=0)
    app.insts.grid(row = 5, column = 0, columnspan=2, ipadx=26)
    app.insts.bind('<<ListboxSelect>>', app.Display_measures)

    app.alignbut = Button(app, text='align...', command=app.Align_popup)
    app.alignbut.grid(row=1, column=3)

    app.playbut = Button(app, text='play!', command=app.pdplay)
    app.playbut.grid(row=2, column=2)

    app.printbut = Button(app, text='print...', command=app.Image_popup)
    app.printbut.grid(row=2, column=3)

    app.savebut = Button(app, text='save...', command=app.Save)
    app.savebut.grid(row=3, column=3)
    app.loadbut = Button(app, text='load...', command=app.Load)
    app.loadbut.grid(row=3, column=2)

    app.normbut = Button(app, text='normalize', command=app.Norm)
    app.normbut.grid(row=4, column=2, columnspan=2)

def Build_img(app):
    """Takes main application as argument"""
    pop = Toplevel()
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
    pop.plot = Button(pop, text="print", command= (lambda: app.scheme_dispatcher('generate_image', opacity=pop.opslider.get(), divisions=pop.bpislider.get()))
    pop.plot.grid(row=2, column=1)

def Build_align(app):
    """Takes main application, Toplevel() window as arguments"""
    pop = Toplevel()
    pop.title("align")
    menuinst = []
    [menuinst.append(i) for i in app.scheme.inst]
    
    invarm = StringVar()
    invars = StringVar()
    invarm.set(menuinst[0])
    invars.set(menuinst[0])

    ## drop menus
    pop.primarydrop = OptionMenu(pop, invarm, *(menuinst),
                                command = (lambda invarm: al_box_update(app, pop.primaryalign, invarm)))
    pop.secondarydrop = OptionMenu(pop, invarm, *(menuinst),
                                command = (lambda invarm2: al_box_update(app, pop.secondarydrop, invarm2)))
    pop.replicadrop = OptionMenu(pop, invars, *(menuinst),
                                command = (lambda invars: al_box_update(app, pop.replicaalign, invars)))

    pop.sameprimary = IntVar()
    pop.same = Checkbutton(pop, text="same primary", variable=pop.sameprimary, onvalue=1, offvalue=0)

    pop.primarydrop.grid(row = 0, column=0, columnspan=2)
    pop.same.grid(row=0, column=5, columnspan=1)
    pop.secondarydrop.grid(row = 0, column=4, columnspan=1)
    pop.replicadrop.grid(row=0, column=2, columnspan=2)

    ## listboxes
    pop.primaryalign = Listbox(pop, exportselection=0)
    pop.replicaalign = Listbox(pop, exportselection=0)
    pop.secondaryalign = Listbox(pop, exportselection=0)

    pop.primaryalign.grid(row=1, column=0, columnspan=2)
    pop.replicaalign.grid(row=1, column=2, columnspan=2)
    pop.secondaryalign.grid(row=1, column=4, columnspan=2)

    for i in app.inst[app.inst.index(0)]:
        pop.primaryalign.insert(END, i.beatstr)
        pop.replicaalign.insert(END, i.beatstr)
        pop.secondaryalign.insert(END, i.beatstr)

    pop.primarypivot = Entry(pop)
    pop.replicapivot = Entry(pop)
    pop.primarypivot2 = Entry(pop)
    pop.replicapivot2 = Entry(pop)

    pop.primarypivot.grid(row=2, column=1)
    pop.replicapivot.grid(row=2, column=3)
    pop.primarypivot2.grid(row=2, column=5)
    pop.replicapivot2.grid(row=3, column=3)

    pop.pivotp = Label(pop, text="p pivot beat")
    pop.pivotr = Label(pop, text="r pivot beat")
    pop.pivotp2 = Label(pop, text="p2 anchor")
    pop.pivotr2 = Label(pop, text="replica endpoint")

    pop.pivotp.grid(row=2, column=0)
    pop.pivotr.grid(row=2, column=2)
    pop.pivotp2.grid(row=2, column=4)
    pop.pivotr2.grid(row=3, column=2)
   
    pop.goalign = Button(pop, text='align!', command= (lambda: al_final(app, pop)))
    pop.goalign.grid(row=1, column=7)
    #pop.tweakm = Entry(pop)
    #pop.tweakm.grid(row=3, column=1)
    #pop.tweakmlab = Label(pop, text="master endpoint")
    #pop.tweakmlab.grid(row=3, column=0)

    pop.gotweak = Button(pop, text='anchor to pt', command= (lambda: tw_final(app, pop)))
    pop.gotweak.grid(row=2, column=7)
    pop.gopad = Button(pop, text='pad to pt', command= (lambda: pad_final(app, pop)))
    pop.gopad.grid(row=0, column=7)

    pop.chs = IntVar()
    pop.che = IntVar()
    pop.chstart = Checkbutton(pop, text="anchor start", variable=pop.chs, onvalue=1, offvalue=0)
    pop.chend = Checkbutton(pop, text="anchor end", variable=pop.che, onvalue=2, offvalue=0)
    pop.statlab = Button(pop, text="global pt", command= (lambda: basic_align(app,pop)))
    pop.static = Entry(pop)

    pop.chstart.grid(row=0, column=6)
    pop.chend.grid(row=1, column=6)
    pop.statlab.grid(row=2, column=6)
    pop.static.grid(row=3, column=6)

def create_final(app):
    inst = app.insts.get(ACTIVE)[0]
    st = app.st.get()
    end = app.end.get()
    length = app.long.get()
    if '' in [inst, st, end, length]:
        print 'enter all required measure info'
    else:
        app.scheme_dispatcher('command', instrument=inst, start=st, end=end, time=length)

def al_box_update(app, box, whichinst):
    """takes app, Listbox to update, and instrument name as string"""
    box.delete(0, END)
    for i in app.inst:
        if i == whichinst:
            for j in app.inst[i]:
                box.insert(END, j.beatstr)

def al_final(app, pop):
    try:
        pm = app.scheme.inst[pop.primarydrop.cget("text")][pop.primaryalign.curselection()[0]]
        rm = app.scheme.inst[pop.replicadrop.cget("text")][pop.primaryalign.curselection()[0]]
    except IndexError:
        print 'instrument/measure selections incorrect'
    ppt = pop.primarypivot.get()
    rpt = pop.replicapivot.get()
    if ppt=='' or rpt=='':
        return
    if ppt.lower()=='start':
        ppt = 0
    elif ppt.lower()=='end':
        ppt = pm.timesig
    if rpt.lower()=='start':
        sp = 0
    elif rpt.lower()=='end':
        sp = rm.timesig

    try:
        ppt = int(ppt)
        rpt = int(rpt)
    except ValueError:
        print "enter 'start', 'end', or a beat number"
   
    app.scheme_dispatcher('align', pm, rm, ppt, rpt)

def tw_final(app, pop):
    #########################_____________________________
    ppt = pop.primarypivot.get()
    rpt = pop.replicapivot.get()
    ppt2 = pop.primarypivot2.get()
    rpt2 = pop.replicapivot2.get()
    dir = pop.chs.get() + pop.che.get() #(neither, start, end, or both)
    try:
        pm = app.inst[pop.primarydrop.cget("text")][pop.primaryalign.get(ACTIVE)[0]]
        rm = app.inst[pop.replicadrop.cget("text")][pop.replicaalign.get(ACTIVE)[0]]
    except IndexError:
        print 'choose two instruments!'
        pass

    if pop.sameprimary.get() == 0:
        try:
            sm = app.scheme.inst[pop.secondarydrop.cget("text")][int(pop.secondaryalign.curselection()[0])]
        except IndexError:
            print 'select a secondary instrument or check the samemaster box!'
            pass
    else:
        sm = pm
    pts = [ppt, rpt, ppt2, rpt2]
    if '' in pts
        pass
    else:
        app.scheme_dispatcher('tweak', pm, rm, sm, pts, dir)

def pad_final(app, pop):
#####################
    pm = app.scheme.inst[pop.primarydrop.cget("text")][int(pop.primaryalign.curselection()[0])]
    rm = app.scheme.inst[pop.replicadrop.cget("text")][int(pop.replicaalign.curselection()[0])]

    pts = [float(pop.primaryalign.curselection()[0]), float(pop.replicaalign.curselection()[0]), pop.primarypivot.get()]
    if '' in pts:
        pass
    else:
        app.scheme_dispatcher('pad', app.scheme.inst[pop],
                  app.scheme.inst[pop.replicadrop.cget("text")], pop.tweakend.get())

def Build_inst(app):
    """Takes main application, Toplevel() window as arguments"""
    pop = Toplevel()
    pop.title("instrument manager")

    pop.ilab = Label(pop, text='instrument name', relief=RAISED)
    pop.ilab.grid(row=0, column=0)
    pop.iname = Entry(pop)
    pop.iname.grid(row=0, column=1)
    pop.igo = Button(pop, text='add instrument',
                     command=(lambda: app.scheme_dispatcher('create_inst', name=str(pop.iname.get()))))
    pop.igo.grid(row=0, column=2)
    pop.ilist = Listbox(pop, exportselection=0)
    pop.ilist.grid(row=1, column=0, columnspan=2)
    for i in app.scheme.inst:
        pop.ilist.insert(END, i)
    pop.idel = Button(pop, text='delete instrument',
                      command=(lambda: app.scheme_dispatcher('del_inst', name=pop.ilist.curselection()[0]))))
    pop.idel.grid(row=2, column=1)

def Clear(app):
    """clears entry boxes after file change or function call"""
    app.st.delete(0, END)
    app.end.delete(0, END)
    app.long.delete(0, END)
    app.rhy.delete(0, END)

