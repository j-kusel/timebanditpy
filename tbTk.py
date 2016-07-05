from Tkinter import *

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
        
    app.opslider = Scale(pop, from_=0, to=100)
    app.opslider.grid(row=0, column=0)
    app.bpislider = Scale(pop, from_=1, to=10)
    app.bpislider.grid(row=1, column=0)
    app.plot = Button(pop, text="print", command=app.imggen)
    app.plot.grid(row=0, column=1)

def Build_align(app, pop):
    """Takes main application, Toplevel() window as arguments"""
    
    pop.title("align")

    app.masteralign = Listbox(pop, exportselection=0)
    app.slavealign = Listbox(pop, exportselection=0)
    app.masteralign.grid(row=0, column=0)
    app.slavealign.grid(row=0, column=1)

    app.pivotmaster = Entry(pop)
    app.pivotslave = Entry(pop)
    app.pivotmaster.grid(row=1, column=0)
    app.pivotslave.grid(row=1, column=1)

    app.goalign = Button(pop, text='align!', command=app.Final_align)
    app.goalign.grid(row=1, column=2)

def Clear(app):
    """clears entry boxes after file change or function call"""
    app.st.delete(0, END)
    app.end.delete(0, END)
    app.long.delete(0, END)
    app.rhy.delete(0, END)
