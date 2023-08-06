#beige!/usr/bin/env python3
import sqlite3
import os
import sys
import time
from tkinter import *
from tkinter import ttk

def OnDoubleClick(event):
        widget = event.widget
        item = widget.selection()
        print(item)
        for i in item:
                print("you clicked on", widget.item(i,"text"), widget.item(i,"values"))

def restartme():
        fh = open('mytest01.py', 'rb')
        fh1 = open('mytest02.py', 'wb')
        fh1.write(fh.read())
        fh.close()
        fh1.close()
        #os.system('chmod +x mystest02.py')
        os.execl(sys.executable, sys.executable, 'mytest02.py')
        
        
dbfile = 'apodixispro/data/apodixispro.db'
if not os.path.exists(dbfile):
        dbfile = r'C:\Users\Konstas\AppData\Roaming\.apodixispro\data\apodixispro.db'
        # dbfile =r'C:\Users\Konstas\workspace\apodixis\data\apodixis.db'
query = 'select afm, eponimia, thlefono from epixirisis order by eponimia'
query1 = 'select aa, afm, ddate, poso from apodixis order by oik_etos'
lis = []

syn = sqlite3.connect(dbfile)
cur = syn.cursor()
cur.execute(query1)

for line in cur.fetchall():
	lis.append(line)	

tv = ttk.Treeview()
#tv['columns'] = ('eponimia', 'thlefono')
tv['columns'] = ('afm', 'ddate', 'poso')

#tv.insert('', END, 'gon', text='Επιχειρήσεις')
tv.insert('', END, 'gon', text='Αποδείξεις new')

tv.grid(row=0, column=0, columnspan=2)
vsbar = ttk.Scrollbar( orient="vertical", command=tv.yview)
vsbar.grid(row=0, column=2, sticky=N+S)

tv.configure(height=30, yscrollcommand=vsbar.set, selectmode=EXTENDED)
tv.column('#0', minwidth=80, width=80)
##tv.column('eponimia', width=600)
count = 1
for item in lis:
        if count % 2 == 0:
                tv.insert('gon', END, text=item[0], values=(item[1], item[2], item[3]), tags=('oddrow',))
        else:
                tv.insert('gon', END, text=item[0], values=(item[1], item[2], item[3]), tags=('evenrow',))
        count += 1
# print(count)
tv.grid_configure(sticky=N+S+W+E)
tv.columnconfigure(0, weight=1)
tv.rowconfigure(0, weight=1)
tv.tag_configure('oddrow', background='cyan')
tv.tag_configure('evenrow', background='maroon')

tv.bind('<Double-1>', OnDoubleClick)
tv.bind('<Button-2>', OnDoubleClick)

btnRest = ttk.Button(text='Restart Me', command=restartme)
btnRest.grid(row=1, column=0)

btncls = ttk.Button(text='Close', command=sys.exit)
btncls.grid(row=1, column=1)



p = tv.winfo_toplevel()
p.resizable(width=750, height=40)
p.columnconfigure(0, weight=1)
p.rowconfigure(0, weight=1)
p.title('Επιχειρήσεις')
p.update()
print(os.getpid())
#restartme()
mainloop()
