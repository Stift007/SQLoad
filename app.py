import sqlite3
from tkinter import *
from tkinter import filedialog,messagebox,simpledialog
from tkinter.ttk import Notebook, Frame, Treeview
import os
import sys

try:
    file = sys.argv[1]
except:
    file=None


root = Tk()
root.title("SQLoad3 GUI")
root.geometry("500x500")
root.iconbitmap('sql.ico')

def singleline():
    code = simpledialog.askstring('SQL Line','Execute (And directly commit) 1 Line of SQL Code')
    saveToDb(code)

def editor():
    tl = Toplevel(root)
    tl.iconbitmap('sql.ico')
    tlmenu = Menu(tl)
    tlfilemenu = Menu(tlmenu,tearoff=0)
    tlfilemenu.add_command(label='Commit Changes',command=lambda: saveToDb(text.get('1.0',END)))
    tlmenu.add_cascade(menu=tlfilemenu,label='File')
    tl.config(menu=tlmenu)
    tl.title("SQLoad3 Editor")
    tl.geometry("500x500")
    text = Text(tl)
    text.pack()
    tl.mainloop()

def saveToDb(code):
    try:
        cur = db.cursor()
        for statement in code.split(";"):
            try:
                cur.execute(statement)
            except Exception as error:
                messagebox.showerror('Commit Failed',error)
        db.commit()
        messagebox.showinfo('Commit Notice',f'Commited {len(code.split(";"))} Statements')
    except Exception as error:
        messagebox.showerror('Commit Failed',error)

def browseDbFiles():
    filename = filedialog.askopenfilename(defaultextension="*.db",filetypes=[
        ("SQL Databases","*.db"),
        # ("Schemas",("*.sql","*.edb")),
        ("All Files","*.*")
    ])

    return filename

def browse():
    global db
    name = browseDbFiles()
    if name.endswith(".db"):
        db = sqlite3.connect(name)
        generate_tree()



nb = Notebook(root,width=455,height=455)
dbtab = Frame(nb,width=450,height=450)
nb.add(dbtab,text='Database Overview')
nb.pack()

def generate_tree():
    global tree
    try:
        tree.destroy()
    except:
        ...
    
    tree = Treeview(dbtab)
    
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    maintb = tables[0]
    cursor.execute(f"""
    PRAGMA table_info({maintb[0]});
    """
    )
    columns = cursor.fetchall()
    truecolumns = []
    for c in columns:
        truecolumns.append(c[1])
    tree['columns'] = tuple(truecolumns)

    tree.column("#0",width=50,minwidth=25)
    tree.heading("#0",text='Label')
    for c in truecolumns:
        tree.column(c,anchor=W,width=50)
        tree.heading(c,text=c)

    cursor.execute(f'SELECT * FROM {maintb[0]};')
    print(maintb[0])
    all_ = cursor.fetchall()
    print(all_)
    for data in all_:
        tree.insert('','end', iid=all_.index(data),text=all_.index(data),values=tuple(data))
        



    tree.pack(fill="both",expand=1)


def saveIntoFile(code):
    global db
    file = filedialog.asksaveasfilename(filetypes=[
            ('Plain Text',('*.txt','*.log','*.wtx','*.ptx')),
            ('SQL Schemas',('*.sql','*.edb','*.sdb','*.slt')),
            ('All Files','*.*')
            ])
    with open(file,"w") as f:
        f.write(code)

def saveIntoFileAndToDb(code):
    global db
    file = filedialog.asksaveasfilename(filetypes=[
            ('Plain Text',('*.txt','*.log','*.wtx','*.ptx')),
            ('SQL Schemas',('*.sql','*.edb','*.sdb','*.slt')),
            ('All Files','*.*')
            ])
    with open(file,"w") as f:
        f.write(code)

    db = sqlite3.connect(os.path.splitext(file)[0]+".db")
    saveToDb(code)

def editor2():
    tl = Toplevel(root)
    tl.iconbitmap('sql.ico')
    tlmenu = Menu(tl)
    tlfilemenu = Menu(tlmenu,tearoff=0)
    tlfilemenu.add_command(label='Save and commit...',command=lambda: saveIntoFileAndToDb(text.get('1.0',END)))
    tlfilemenu.add_command(label='Save without commit...',command=lambda: saveIntoFile(text.get('1.0',END)))
    tlmenu.add_cascade(menu=tlfilemenu,label='File')
    tl.config(menu=tlmenu)
    tl.title("SQLoad3 Editor")
    tl.geometry("500x500")
    text = Text(tl)
    text.pack()
    tl.mainloop()

menubar = Menu(root)
filemenu = Menu(menubar,tearoff=0)
filemenu.add_command(command=browse,label='Open')
filemenu.add_command(command=generate_tree,label='Refresh')
edmen = Menu(menubar,tearoff=0)
edmen.add_command(command=editor,label='Open raw SQL Editor')
edmen.add_command(command=editor2,label='Create new SQL Schema')
edmen.add_command(command=singleline,label='Execute single SQL Statement')

menubar.add_cascade(label='File',menu=filemenu)
menubar.add_cascade(label='SQL',menu=edmen)
root.config(menu=menubar)


if file:
    global db
    if file.endswith(".db"):
        db = sqlite3.connect(file)
        generate_tree()

root.mainloop()