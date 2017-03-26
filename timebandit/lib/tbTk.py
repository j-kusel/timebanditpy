from Tkinter import *

from collections import OrderedDict

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
    menu.add_command(label='add inst...', command=(lambda: Build_inst(app)))
    menu.add_command(label='align...', command=(lambda: Build_align(app)))
    #menu.add_command(label='evaluate...', command=(lambda: Build_network(app)))
    menu.add_command(label='preferences...')

    menu = Menu(app.menubar, tearoff=0)
    app.menubar.add_cascade(label='playback', menu=menu)
    menu.add_command(label='network...', command=(lambda: Build_network(app)))

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

    app.go = Button(app, text="go", command=(lambda: create_final(app)), padx = 96)
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

    def Display_measures(_event):
        app.bars.delete(0, END)
        if len(app.scheme.inst) != 0:
            for i in app.scheme.inst[app.insts.get(app.insts.curselection()[0])]:
                app.bars.insert(END, i)

    app.insts.bind('<<ListboxSelect>>', Display_measures)

    app.alignbut = Button(app, text='align...', command=(lambda: Build_align(app)))
    app.alignbut.grid(row=1, column=3)

    app.netbut = Button(app, text='network...', command=(lambda: Build_network(app)))
    app.netbut.grid(row=2, column=2)

    app.printbut = Button(app, text='print...', command=(lambda: Build_img(app)))
    app.printbut.grid(row=2, column=3)

    app.savebut = Button(app, text='save...', command=app.Save)
    app.savebut.grid(row=3, column=3)
    app.loadbut = Button(app, text='load...', command=app.Load)
    app.loadbut.grid(row=3, column=2)

    app.normbut = Button(app, text='normalize', command=(lambda: norm(app)))
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
    pop.plot = Button(pop, text="print", command= (lambda: app.scheme_dispatcher('generate_image', opacity=pop.opslider.get(), divisions=pop.bpislider.get())))
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

    for i in app.scheme.inst[app.insts.get(ACTIVE)]:
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
    ###### vvvvvvvv
    pop.statlab = Button(pop, text="global pt", command= (lambda: al_final(app,pop)))
    pop.static = Entry(pop)

    pop.chstart.grid(row=0, column=6)
    pop.chend.grid(row=1, column=6)
    pop.statlab.grid(row=2, column=6)
    pop.static.grid(row=3, column=6)

def Build_network(app):
    pop = Toplevel()
    pop.title('network')
    pop.insts = []
    pop.ports = []
    pop.channels = []
    pop.mutes = []
    pop.checkvars = []
    i = 0
    for inst in app.scheme.inst:
        print inst + 'network build'
        pop.insts.append(Label(pop, text=inst))
        pop.insts[i].grid(row=i, column=0)
        pop.ports.append(Entry(pop))
        pop.ports[i].grid(row=i, column=1)
        pop.ports[i].insert(0, str(8100+i))
        pop.channels.append(Entry(pop))
        pop.channels[i].grid(row=i, column=2)
        pop.channels[i].insert(0, str(0))

        pop.checkvars.append(IntVar())
        pop.mutes.append(Checkbutton(pop, text='M', variable=pop.checkvars[-1]))
        pop.mutes[i].grid(row=i, column=3)
        i += 1
    pop.server = Button(pop, text='start server', command = (lambda: start_network(app, pop)))
    pop.server.grid(row=0, column=4, columnspan=3)
    pop.kill = Button(pop, text='disconnect server', command = (lambda: end_network(app, pop)))
    pop.kill.grid(row=1, column=4, columnspan=3)

    pop.play = Button(pop, text='play', command = (lambda: final_network_command(app, 'play')))
    pop.play.grid(row=3, column=4)
    pop.pause = Button(pop, text='pause', command = (lambda: final_network_command(app, 'pause')))
    pop.pause.grid(row=3, column=5)
    pop.stop = Button(pop, text='stop', command = (lambda: final_network_command(app, 'stop')))
    pop.stop.grid(row=3, column=6)

    pop.transport = Entry(pop)
    pop.transport.grid(row=4, column=4)
    #pop.tr_samp = Button(pop, text='samples', command = (lambda: final_network_transport(app, 'samp', pop.transport.get())))
    pop.tr_ms = Button(pop, text='milliseconds', command = (lambda: final_network_transport(app, pop.transport.get())))
    #pop.tr_samp.grid(row=4, column=5)
    pop.tr_ms.grid(row=4, column=5, columnspan=2)

def start_network(app, pop):
    #ports = [[int(i) for i in str(p.get()).split()] for p in pop.ports]
    ports = OrderedDict()
    channels = OrderedDict()
    i = 0
    print app.scheme.inst, "scheme"
    indices = []
    for inst in app.scheme.inst:
        ports[inst] = [int(p) for p in str(pop.ports[i].get()).split()]
        channels[inst] = [int(c) for c in str(pop.channels[i].get()).split()]
        i += 1
    app.scheme.start_server(ports=ports, channels=channels)        

def end_network(app, pop):
    app.scheme.end_server()

def final_network_command(app, msg):
    app.scheme.network_command(msg)

def final_network_transport(app, location):
    app.scheme.network_transport(location)

def create_final(app):
    inst = app.insts.get(ACTIVE)
    st = app.st.get()
    end = app.end.get()
    length = app.long.get()
    if '' in [inst, st, end, length]:
        print 'enter all required measure info'
    else:
        app.scheme_dispatcher('create', instrument=inst, start=int(st), end=int(end), time=int(length))
        refresh(app)

def norm(app):
    """adjust offsets so there are no negative timecodes"""
    app.scheme_dispatcher('normalize', instrument=app.insts.get(ACTIVE), measure=int(app.bars.curselection()[0]))
    refresh(app)

def al_box_update(app, box, whichinst):
    """takes app, Listbox to update, and instrument name as string"""
    box.delete(0, END)
    for m in app.scheme.inst[whichinst]:
        box.insert(END, m.beatstr)

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
   
    app.scheme_dispatcher('align', primary_meas=pm, replica_meas=rm, primary_point=ppt, replica_point=rpt)
    refresh(app)

def tw_final(app, pop):
    #########################_____________________________
    ppt = pop.primarypivot.get()
    rpt = pop.replicapivot.get()
    ppt2 = pop.primarypivot2.get()
    rpt2 = pop.replicapivot2.get()
    dir = pop.chs.get() + pop.che.get() #(neither, start, end, or both)
    try:
        pm = app.scheme.inst[pop.primarydrop.cget("text")][pop.primaryalign.curselection()[0]]
        rm = app.scheme.inst[pop.replicadrop.cget("text")][pop.replicaalign.curselection()[0]]
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
    try:
        pts = [float(x) for x in [ppt, rpt, ppt2, rpt2]]
        app.scheme_dispatcher('tweak', primary_meas=pm, replica_meas=rm, secondary_meas=sm, points=pts, direction=dir)
        pop.destroy()
        refresh(app)
    except ValueError:
        print 'enter all necessary information for tweaking measures'

def pad_final(app, pop):
#####################
    pm = app.scheme.inst[pop.primarydrop.cget("text")][int(pop.primaryalign.curselection()[0])]
    rm = app.scheme.inst[pop.replicadrop.cget("text")][int(pop.replicaalign.curselection()[0])]
    pts = [pop.primarypivot.get(), pop.primarypivot2.get()]
    ### add 'start'/'end' crap here
    try:
        pts = [int(i) for i in pts]
        app.scheme_dispatcher('pad', primary_meas=pm, replica_meas=rm, points=pts)
        refresh(app)
        pop.destroy()
    except ValueError:
        print "enter all necessary padding information"

def Build_inst(app):
    """Takes main application, Toplevel() window as arguments"""
    pop = Toplevel()
    pop.title("instrument manager")

    pop.ilab = Label(pop, text='instrument name', relief=RAISED)
    pop.ilab.grid(row=0, column=0)
    pop.iname = Entry(pop)
    pop.iname.grid(row=0, column=1)
    pop.igo = Button(pop, text='add instrument',
                     command=(lambda: inst_create_final(app, pop)))
    pop.igo.grid(row=0, column=2)
    pop.ilist = Listbox(pop, exportselection=0)
    pop.ilist.grid(row=1, column=0, columnspan=2)
    for i in app.scheme.inst:
        pop.ilist.insert(END, i)
    pop.idel = Button(pop, text='delete instrument',
                      command=(lambda: inst_del_final(app, pop)))
    pop.idel.grid(row=2, column=1)

def inst_create_final(app, pop):
    app.scheme_dispatcher('create_inst', name=str(pop.iname.get()))
    pop.ilist.delete(0, END)
    for i in app.scheme.inst:
        pop.ilist.insert(END, i)
    refresh(app)

def inst_del_final(app, pop):
    app.scheme_dispatcher('del_inst', name=pop.ilist.get(ACTIVE))
    pop.ilist.delete(0, END)
    pop.iname.delete(0, END)
    for i in app.scheme.inst:
        pop.ilist.insert(END, i)
    refresh(app)

def refresh(app):
    inst_select = app.insts.get(ACTIVE)
    app.st.delete(0, END)
    app.end.delete(0, END)
    app.long.delete(0, END)
    app.rhy.delete(0, END)
    app.insts.delete(0, END)
    app.bars.delete(0, END)
    for i in app.scheme.inst:
        app.insts.insert(END, i)
        if i == inst_select:
            for m in app.scheme.inst[i]:
                app.bars.insert(END, m)
