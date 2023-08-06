#!/usr/bin/env python3
#-*- coding: utf-8 -*-
#==================================================================================
#  Copyright:
#
#      Copyright (C) 2013 Konstas Marmatakis <marmako@gmail.com>
#
#   License:
#
#      This program is free software; you can redistribute it and/or modify
#      it under the terms of the GNU General Public License version 3 as
#      published by the Free Software Foundation.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this package; if not, write to the Free Software
#      Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#==================================================================================

import locale
import gettext
import zipfile
import tarfile
import time
import os
import threading

from datetime import datetime, date
from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter.filedialog import askopenfilename, askopenfilenames,  askdirectory, asksaveasfilename
from tkinter.messagebox import askyesno, showinfo

from backup import checkversion
from backup import backup
from backup.backup import create_dirs, dir_name


ALL = N+S+E+W


##print(len(sys.argv), sys.argv[0])
# print(sys.argv[0])
# abspath = os.path.abspath(sys.argv[0])
dir_name = os.path.dirname(__file__)
# os.chdir(dir_name)
# print(dir_name)

glossa = locale.getdefaultlocale()[0]
print(glossa)

##if sys.platform.startswith("win"):
##    
##    loc = locale.getlocale()
##    locale.setlocale(locale.LC_ALL, loc)

t = gettext.translation("tkbak", localedir=os.path.join(dir_name, "locale"), codeset='utf-8', fallback=True, \
                        languages=[glossa]) # t = Translation.
_ = t.gettext
t.install()



class GuiBackup:
    def __init__(self, parent=None, title=_('tkbak Backup Application')):
        self.parent = parent
        self.msg = StringVar()
        self.lis = []
        self.minima = StringVar()
        self.typefile = StringVar()
        self.filemode = StringVar()
        self.project_name = StringVar()
        self.project_loaded = False
        self.title = title
        self.parent.title(self.title)
        self.parent.iconname('tkbak')
        self.create_icon(self.parent)
        self.maketoolbar()
        self.makewidgets()
        self.makebottomtoolbar()
        self.parent.update_idletasks()
        self.center_window(self.parent)
        self.parent.protocol("WM_DELETE_WINDOW", lambda: '')
        self.checkload()
        self.parent.after_idle(self.check_ver)
        
   
    def check_ver(self):
        sys.stdout = self
        v = checkversion.check_version()
        if v:
            # msg = _("New version is available. Version: {0}\nYou can download it at {1}").format(v, 'https://testpypi.python.org/pypi/tkbak')
            msg = _("New version is available. Version: {0}\nDo you want to download it now?").format(v)
            if askyesno(self.title, msg):

                checkversion.downloadthefile(v)
        sys.stdout = sys.__stdout__
            
    def create_icon(self, p):
        #Try to set icon.
        try:
            p.iconbitmap('@' + dir_name + os.sep + 'docs/wilber_painter.xbm')
        except:
            img = PhotoImage(file=dir_name + os.sep  + 'docs/tkbak.gif')
            p.tk.call('wm', 'iconphoto', p._w, img)


    def center_window(self, afentiko):
        width = afentiko.winfo_width()
        height = afentiko.winfo_height()
        sw = afentiko.winfo_screenwidth()
        sh = afentiko.winfo_screenheight()
        afentiko.geometry("%dx%d%+d%+d" % (width, height, sw/2-width/2, sh/2-height/2))


    def maketoolbar(self):
        #st = ttk.Style()
        #st.configure("f.TFrame", background='black')

        toolbar = ttk.Frame(self.parent)
        toolbar.grid(row=0, column=0, sticky=W+E)
        
        loadbtn = ttk.Button(toolbar, text=_('Load Previous Files'), command=self.loadme)
        loadbtn.grid(row=0, column=0, sticky=W)
        self.loadbtn = loadbtn
        
        btncreat_project = ttk.Button(toolbar, text=_('Create Project File'), command=self.create_project)
        btncreat_project.grid(row=0, column=1)
        self.btncret_project = btncreat_project
#         self.btncret_project['state'] = DISABLED
        
        btnload_project = ttk.Button(toolbar, text=_('Load Project File'), command=self.read_project)
        btnload_project.grid(row=0, column=2)
        self.btnload_project = btnload_project
#         self.btnload_project['state'] = DISABLED
        
        btnlisf = ttk.Button(toolbar, text=_('Add Files'), command=lambda: self.appendlis())
        btnlisf.grid(row=0, column=3)
        self.btnlisf = btnlisf
        
        btnlisd = ttk.Button(toolbar, text=_('Add Directories'), command=lambda: self.appendlis(2))
        btnlisd.grid(row=0, column=4)
        self.btnlisd = btnlisd
        
        btncopyr = ttk.Button(toolbar, text=_('License...'), command=showlicense)
        btncopyr.grid(row=0, column=5)
        
        btnmnia = ttk.Button(toolbar, text=_('Credits'), command=self.credits)
        btnmnia.grid(row=0, column=6)
        
#         btnreadme = ttk.Button(toolbar, text=_('README'), command=self.readme)
#         btnreadme.grid(row=0, column=7)
    
        for child in toolbar.winfo_children():
            child.grid_configure(pady=4, padx=4)
    
        for x in range(toolbar.grid_size()[0]-1):
            toolbar.columnconfigure(x, weight=1)
        #for x in range(toolbar.grid_size()[1]-1):
        #    toolbar.rowconfigure(x,weight=1)


    def makebottomtoolbar(self):
        #st = ttk.Style()
        #st.configure("f.TFrame", background='black')
        btoolbar = ttk.Frame(self.parent)
        btoolbar.grid(row=2, column=0, sticky=W+E)

        impfilebtn = ttk.Button(btoolbar, text=_("Target file"), command= self.impfile)
        impfilebtn.grid(row=0, column=0, sticky=W)
        self.impfilebtn =impfilebtn

        strtbtn = ttk.Button(btoolbar, text=_('Start'), command=self.run_script)
        strtbtn.grid(row=0, column=0, sticky=E)
        self.strtbtn = strtbtn

        btnrestore = ttk.Button(btoolbar, text=_('Restore from backup'), command=self.restoreform)
        btnrestore.grid(row=0, column=2)
        self.btnrestore = btnrestore

        clsbtn = ttk.Button(btoolbar, text=_('Close'), command=self.closeme)
        clsbtn.grid(row=0, column=3, sticky=E)
        self.clsbtn = clsbtn
        
        for child in btoolbar.winfo_children():
            child.grid_configure(pady=4, padx=4)
    
        for x in range(btoolbar.grid_size()[0]-1):
            btoolbar.columnconfigure(x, weight=1)
        for x in range(btoolbar.grid_size()[1]-1):
            btoolbar.rowconfigure(x,weight=1)

    
    def makewidgets(self):
        frm = ttk.Frame(self.parent)
        frm.grid(row=1, column=0, sticky=ALL)
    
        tex = ScrolledText(frm, width=70, height=20, bg='black', fg='green')
        tex.grid(row=1, column=2, rowspan=2, sticky=ALL)
        msg = _('Backup Application')
        tex.insert(END, msg.center(70, '*'))
        tex.tag_add('protigrammi', '1.0', '1.end')
        tex.tag_config('protigrammi', background='green', foreground='black')
#         tex.tag_add('ln', '2.0')
        tex.tag_bind('protigrammi', '<Double-1>', self.creditbind)
        tex.config(state=DISABLED)
        self.tex = tex

        lblfrm1 = ttk.LabelFrame(frm, text=_('Files'))
        lblfrm1.grid(row=1, column=0, sticky=ALL)
        lblfrm1.columnconfigure(0, weight=1)

        lboxfiles = Listbox(lblfrm1, width=40, height=10, selectmode=EXTENDED)
        lboxfiles.grid(row=0, column=0, sticky=ALL)
        self.lboxfiles = lboxfiles
        self.lboxfiles.bind('<Double-1>', self.OnDouble) #Να το παιδέψω.
        self.lboxfiles.bind('<Button-3>', self.OnDouble)
        vsb01 = ttk.Scrollbar(lblfrm1, orient="vertical", command=self.lboxfiles.yview)
        self.lboxfiles.configure(yscrollcommand=vsb01.set)
        vsb01.grid(row=0, column=1, sticky=N+S)
#         btndel1 = ttk.Button(lblfrm1, text='Διαγραφή Επιλεγμένου', command=lambda: self.del_frm_list(None, self.lboxfiles))
#         btndel1.grid(sticky=S)

        lblfrm2 = ttk.LabelFrame(frm, text=_('Directories'))
        lblfrm2.grid(row=2, column=0, sticky=ALL)
        lblfrm2.columnconfigure(0, weight=1)

        lboxdirs = Listbox(lblfrm2, width=40, height=10, selectmode=EXTENDED)
        lboxdirs.grid(row=0, column=0, stick=ALL)
        self.lboxdirs = lboxdirs
        self.lboxdirs.bind('<Double-1>', self.OnDouble)
        self.lboxdirs.bind('<Button-3>', self.OnDouble)
        vsb = ttk.Scrollbar(lblfrm2, orient='vertical', command=self.lboxdirs.yview)
        self.lboxdirs.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky=N+S)

        lblfrmradio = ttk.LabelFrame(frm, text=_('Select File Type'))
        lblfrmradio.grid(row=1, column=3, sticky=N)

        rdiozip = ttk.Radiobutton(lblfrmradio, width=20, text= _('Zip File'), command=lambda:self.change_filename(self.ent.get()), variable=self.typefile, value='typezip')
        rdiozip.grid(row=0, column=0)

        rdiotar = ttk.Radiobutton(lblfrmradio, width=20, text=_('Tar File'), command=lambda: self.change_filename(self.ent.get()),  variable=self.typefile, value='typetar')
        rdiotar.grid(row=1, column=0)

        self.typefile.set('typezip')

        lblfrmmode = ttk.Labelframe(frm, text=_('Open File'))
        lblfrmmode.grid(row=1, column=3, sticky=S)

        rdioappend = ttk.Radiobutton(lblfrmmode, text=_('add files and comments'), variable=self.filemode, value='a')
        rdioappend.grid(row=0, column=0, sticky=W)

        rdiowrite = ttk.Radiobutton(lblfrmmode, text=_('new for add files'), variable=self.filemode, value='w')
        rdiowrite.grid(row=1, column=0, sticky=W)

        self.filemode.set('w')
        
        ent = ttk.Entry(frm)
        ent.grid(row=4, column=0, columnspan=2, sticky=W+E)
        ent.insert(0, os.path.normpath(os.path.join(os.path.expanduser('~'),'zip.zip')))
        self.ent = ent

#         defaultchk = ttk.Checkbutton(frm, text=_('Most recent file'), state=DISABLED, command='')
#         defaultchk.grid(row=1, column=3, sticky=W+E)

        sp1 = ttk.Separator(frm)
        sp1.grid(row=3, column=0, columnspan=4, sticky=W+E)

        lbl = ttk.Label(frm, textvariable = self.msg)
        lbl.grid(row=4, column=2, sticky=N+S+W+E)

        sp2 = ttk.Separator(frm)
        sp2.grid(row=5, column=0, columnspan=4, sticky=W+E)

#         lblcomment = ttk.Label(frm, text = _('Write your comment:'))
#         lblcomment.grid(row=2, column=3, sticky=N+W+E)
        lblfrmaddcomment = ttk.LabelFrame(frm, text= _('Write your comment:'))
        lblfrmaddcomment.grid(row=2, column=3, sticky=W)
        
        entcomment = ttk.Entry(lblfrmaddcomment, width=30)
        entcomment.grid(row=2, column=3, sticky=W)
        self.entcomment = entcomment

        for child in frm.winfo_children():
            child.grid_configure(pady=4, padx=4)

        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(1, weight=1)

        for x in range(frm.grid_size()[0]-1):
            frm.columnconfigure(x, weight=1)
        for x in range(frm.grid_size()[1]-1):
            frm.rowconfigure(x,weight=1)

        self.parent.update_idletasks()

    def create_project(self, proj_name=''):
        """Creates a project file that includes
        directories and files. Easy to remember easy to use.
        """
        import dbm
        
        the_path = os.path.join(create_dirs(), 'projects')
        
        ft = [('tkbak files', '.dat'),
              ('tkbak files', '.db'),
              ('All Files', '*')]
        
        if not os.path.exists(the_path):
            os.mkdir(the_path)
        if proj_name == None or proj_name == '':
            p = asksaveasfilename(parent=self.parent, initialdir=the_path, initialfile='project', filetypes=ft)
            if len(p) > 0 or p != '':
                p = os.path.splitext(p)[0]
                project = dbm.open(os.path.normpath(p), 'c')
            else:
                return
        else:
            p = proj_name
            p = os.path.splitext(p)[0]
            project = dbm.open(os.path.normpath(p), 'w')
        
        l = ''
        for item in self.lboxdirs.get(0, END):
            l = l + ' ' + item 
        project['directories'] = l
        
        l = ''
        for item in self.lboxfiles.get(0, END):
            l = l + ' ' + item
        project['files'] = l
        project['compressed_file'] = self.ent.get()
        project.sync()
        project.close()
        self.msg.set(_('Project saved: {0}').format(p))
        
    def read_project(self):
        import dbm
        self.lis[:] = []
        ft = [('tkbak files', '.dat'),
              ('tkbak files', '.db'),
              ('All Files', '*')]

        p = askopenfilename(parent=self.parent, initialdir=os.path.join(create_dirs(), 'projects'), \
                              title=self.title, filetypes=ft)
        
        if not p or len(p) == 0:
            return
        p = os.path.splitext(p)[0]
        
        project = dbm.open(os.path.normpath(p), 'w')
        
        dirs = project['directories'].decode()
        self.lboxfiles.delete(0, END)

        for di in dirs.strip().split():
            if os.path.exists(di):
                self.lboxdirs.insert(END, di)
                self.lis.append(di)
            
        
        fils = project['files'].decode()
        self.lboxfiles.delete(0, END)
        for fi in fils.strip().split():
            self.lboxfiles.insert(END, fi)
            self.lis.append(fi)
            
        self.ent.delete(0, END)
        try:
            self.ent.insert(0, project['compressed_file'] )
        except:
            pass
        
        self.project_name = p
        self.msg.set(_('Loaded project: {0}').format(self.project_name))
        self.project_loaded = True
        self.btncret_project['state'] = DISABLED
        self.btnload_project['state'] = DISABLED
        self.loadbtn['state'] = DISABLED

        project.close()

    def creditbind(self, event):
        self.credits()


    def credits(self):
        rtk = Toplevel()
        rtk.wm_attributes('-topmost', 1)
        self.rtk = rtk
        self.create_icon(self.rtk)
#         try:
#             img = PhotoImage(file=dir_name + os.sep  + 'docs/tkbak.gif')
#             self.rtk.tk.call('wm', 'iconphoto', self.rtk._w, img)
#         except:
#             pass
         
        n = ttk.Notebook(self.rtk)
        n.grid(row=0, column=0)
        frm1 = ttk.Frame(n)
        frm1.grid()
        frm2 = ttk.Frame(n)
        frm2.grid()
        frm3 = ttk.Frame(n)
        frm3.grid(sticky=ALL)
        frm3.rowconfigure(0, weight=1)
        frm3.columnconfigure(0, weight=1)

        n.add(frm1, text=_('Programmers'))
        n.add(frm2, text=_('Translators'))
        n.insert(0, frm3, text=_('About'))
        n.select(0)
        n.enable_traversal()

        txtauthors = Text(frm1, width=45, height=10, bg='black', fg='green')
        txtauthors.grid()
        txtauthors.insert(END, open(dir_name + '/docs/AUTHORS').read())
        txtauthors['state'] = DISABLED

        txttranslators = Text(frm2, width=45, height=10, bg='black', fg='green')
        txttranslators.insert(END,  open(dir_name + '/docs/TRANSLATORS').read())
        txttranslators.grid()
        txttranslators['state'] = DISABLED

        style = ttk.Style()
        style.configure("f.TLabel", font=('Arial', 14, 'bold'), foreground='green', background='black', justify=CENTER)
        lblperi = ttk.Label(frm3, anchor=CENTER, style="f.TLabel")
        lblperi.grid(sticky=ALL)
        lblperi['text'] = 'tkbak {0}\n{1}'.format(open(dir_name + '/docs/VERSION').read(), _('Backup and Restore Application')) 

        btnclose = ttk.Button(self.rtk, text=_('Close'), command=rtk.destroy)
        btnclose.grid(row=1, column=0)

        for child in self.rtk.winfo_children():
            child.grid_configure(pady=3, padx=3)
        self.rtk.protocol("WM_DELETE_WINDOW", lambda: '')
        self.rtk.resizable(0, 0)
        self.rtk.update_idletasks()
        self.center_window(self.rtk)

    def change_filename(self, file , expand=True):
        dirpath, filename = os.path.split(file)
        if self.typefile.get() == 'typezip':
            file = filename.split('.')[0] + '.zip'
            self.entcomment['state'] = NORMAL
            if expand == True:
                self.ent.delete(0, END)
                self. ent.insert(0, os.path.normpath(os.path.join(dirpath, file)))
            else:
                return file
        else:
            file = filename.split('.')[0]  + '.tar.gz'
            self.entcomment['state'] = DISABLED
            if expand == True:
                self.ent.delete(0, END)
                self. ent.insert(0, os.path.normpath(os.path.join(dirpath, file)))
            else:
                return file

    def run_script(self):
        
        if len(self.lis) == 0:
            msg = _("No files or directories for archiving.\nPlease load or add files and directories.")
            self.write(msg, True)
            return 1
        
        sys.stdout = self
        self.changestate()
        self.tex['state'] = NORMAL
        dt = datetime.now()
        
        if len(self.entcomment.get()) > 0:
            thecomment = '{0}'.format(self.entcomment.get())
        else:
            thecomment = '{0}'.format(_('Created: ')+dt.strftime('%Y-%m-%d %H:%M:%S'))

        backup.Backup(filesdirs=self.lis, target=self.ent.get(), mode=self.filemode.get(), ftype=self.typefile.get(), \
                      addcom=thecomment)

        sys.stdout = sys.__stdout__

        self.create_recent_files(self.ent.get())
        self.changestate(True)
        self.tex['state'] = DISABLED

    def changestate(self, s=False):
        if s == False:
            self.strtbtn['state'] = DISABLED
            self.clsbtn['state'] = DISABLED
            self.loadbtn['state'] = DISABLED
            self.btnlisf['state'] = DISABLED
            self.btnlisd['state'] = DISABLED
            self.impfilebtn['state'] = DISABLED
            self.btnrestore['state'] = DISABLED
            self.btncret_project['state'] = DISABLED
            self.btnload_project['state'] = DISABLED
            
        else:
            self.clsbtn['state'] = NORMAL
            self.btnlisf['state'] = NORMAL
            self.btnlisd['state'] = NORMAL
            self.impfilebtn['state'] = NORMAL
            self.btnrestore['state'] = NORMAL
            self.btncret_project['state'] = NORMAL
            self.btnload_project['state'] = NORMAL

    def add_comm(self, myzipfile, cc):
            if zipfile.is_zipfile(myzipfile):
                z = zipfile.ZipFile(myzipfile, 'a')
                z.comment = cc.encode('utf-8')
                z.close()
            else:
                self.write(_('The file {0} does not support comments.').format(myzipfile))


    def del_frm_list(self, event, lboxname):
        items = lboxname.curselection()
        pos = 0
        for i in items :
            idx = int(i) - pos
            print(lboxname.get(idx))
            self.lis.remove(lboxname.get(idx))
            lboxname.delete( idx,idx )
            pos = pos + 1

    def OnDouble(self, event):
        widget = event.widget
        selection=widget.curselection()
        #val = widget.get(selection[0])
#        print(_("selection:"), selection, ": '%s'" % val)
        nm = len(selection)
        
        msgplural = t.ngettext('Delete the {0} select item ?', \
                               'Delete the {0} selected items?', nm).format(nm)
        
        if askyesno(self.title, msgplural, default='yes') == True:
            pos = 0
            for item in selection:
                idx = int(item) - pos
                #val = widget.get(item[0])
                print(widget.get(idx))
                val = widget.get(idx)
                widget.delete(idx, idx)
                
                self.lis.remove(val)
                pos += 1
         
    def write(self, minima, addend=False):
        self.tex['state'] = NORMAL
        self.tex.focus_set()
        self.tex.insert(END, minima)
        if addend:
            self.tex.insert(END,'\n')
        self.tex.see(END)
        self.tex.update()
        self.tex['state'] = DISABLED
        try:
            self.msg.set(minima.rstrip('\n'))
        except:
            self.msg.set(minima)
            

    def appendlis(self, fileordir=1):
        #self.parent.withdraw()        
        if fileordir == 1: # File
            p = askopenfilenames(initialdir=os.path.expanduser('~'))
            for itm in self.parent.tk.splitlist(p):
                itm = os.path.normpath(itm)
                if not itm in self.lis:
                    self.lis.append(itm)
                    self.lboxfiles.insert(END, itm)
                else:
                    self.write(_("The file {0} already exists in the list.").format(itm), True)
                            
        elif fileordir == 2: # Directories
            p = os.path.normpath(askdirectory( initialdir=os.path.expanduser('~')))
            if not p in self.lis:
                p = os.path.normpath(p)
                self.lis.append(p)
                self.lboxdirs.insert(END, p)

            else:
                self.write(_("The directory {0} already exists in the list.").format(p), True)
        #self.parent.deiconify()
        
    def loadme(self):
        """ Loads recent files and directories."""
        
        if askyesno(parent=self.parent, title=self.title, message=_('May I load the previous saved source files and directories?'), default='yes') == True:
            p = create_dirs()
            self.loadbtn['state'] = DISABLED
            self.lis[:] = []
            self.lboxfiles.delete(0, END)
            self.lboxdirs.delete(0, END)
            try:
                if os.path.exists(os.path.join(p, 'files.txt')):
                    fp = open(os.path.join(p, 'files.txt'), 'r')
                    text = fp.read()
                    text = text.rstrip('\n')
                    text = text.lstrip('\n')
                    l1 = text.split('\n')
                    for item in l1:
                        if os.path.exists(item):
                            self.lboxfiles.insert(END, item)
                            self.lis.append(item)
                        else:
                            self.write('\n')
                            self.write(_('File {0} doesn\'t exists. Skip it.').format(item))
            except:
                self.tex.insert(END, _('No saved source files.') +'\n')
                self.tex.update()
            finally:
                try:
                    fp.close()
                except:
                    pass
            try:
                if os.path.exists(os.path.join(p, 'dirs.txt')):
                    fp1 = open(os.path.join(p, 'dirs.txt'), 'r')
                    text1 = fp1.read()
                    text1 = text1.rstrip('\n')
                    text1 = text1.lstrip('\n')
                    l2 = text1.split('\n')
                    for item in l2:
                        if os.path.exists(item):
                            self.lboxdirs.insert(END, item)
                            self.lis.append(item)
                        else:
                            self.write(_('Directory {0} doesn\'t exists. Skip it.').format(item), True)
            except:
                self.tex.insert(END, _('No saved source directories.') + '\n')
                self.tex.update()
            finally:
                try:
                    fp1.close()
                except:
                    pass

#     def create_dirs(self):
# 
#         if sys.platform.startswith('win') or sys.platform.endswith('NT'):
#             the_path = os.path.normpath(os.environ['APPDATA']+os.sep+'.tkbak')
#         else:
#             the_path = os.path.normpath(os.path.expanduser('~') + os.sep + '.tkbak')
# 
#         if not os.path.exists(the_path):
#             os.mkdir(the_path)
#         return the_path

    def impfile(self):
        dumpfile =  self.change_filename(time.strftime('%Y%m%d') + '_' + time.strftime('%H%M%S'), False)

        p = asksaveasfilename(parent=self.parent, initialdir=os.path.expanduser('~'), initialfile=dumpfile)
        p = os.path.normpath(p)
        self.ent.delete(0, END)
        self.ent.insert(0, p)
##        self.create_recent_files(p)

    def create_recent_files(self, f):
        p = create_dirs()
        f = os.path.normpath(f)
        lfiles = []
        thefile = os.path.join(p, 'recent_backup_files.txt')
        if os.path.exists(thefile):
            fp = open(thefile, 'r', encoding='utf-8')
            text = fp.read()
            fp.close()
            text = text[:-1]
            fp = open(thefile, 'w', encoding='utf-8')
            for item in text.split('\n'):
                fp.write(item+'\n')
                if not item in lfiles:
                    lfiles.append(item)

            if not f in lfiles:
                lfiles.append(f)
                fp.write(f +'\n')
        else:
            fp = open(thefile, 'w', encoding='utf-8')
            fp.write(f +'\n')
            lfiles.append(f)
        fp.close()
        print(lfiles)
        return lfiles


    def checkload(self):
        p = create_dirs()
        fil1 = os.path.join(p, 'files.txt')
        fil2 = os.path.join(p, 'dirs.txt')
        try:
            text = open(fil1).read()
            if len(text.strip('\n')) == 0:
                os.unlink(fil1)
        except:
            pass
        try:
            text = open(fil2).read()
            if len(text.strip('\n')) == 0:
                os.unlink(fil2)
        except:
            pass

        check1 = os.path.exists(fil1)
        check2 = os.path.exists(fil2)

        if not check1 and not check2:
            self.loadbtn['state'] = DISABLED

    def closeme(self):
        self.tex.config(state=NORMAL)
        if len(self.lis)> 0:
            answer = askyesno(title=self.title, message=_('Do you want to save source files and directories for later use?'), default='yes')
            if answer == True:
                p = os.path.normpath(create_dirs())
                fname = os.path.join(p, 'files.txt')
                try:
                    fp = open(fname, 'w', encoding='utf-8')
                    l = self.lboxfiles.get(0, END)
                    for item in l:
                        fp.write(item+'\n')
                        self.write(_('I am writing the file: {0}').format(item), True)
                        #self.tex.update()
                except:
                    pass
                finally:
                    fp.close()

                try:
                    f = os.path.join(p, 'dirs.txt')
                    fp = open(f, 'w', encoding='utf-8')
                    l2 = self.lboxdirs.get(0, END)
                    for item in l2:
                        fp.write(item +'\n')
                        self.write( _('I am writing the directory: {0}').format(item), True)
                        #self.tex.update()
                except:
                    pass
                finally:
                    fp.close()
        if self.project_loaded:
            self.create_project(self.project_name)
            
        #self.create_project()

        self.write( _('The End.'), True)
        
        self.write( _('Good Buy!!!'), True)
        
        #self.tex.update()
        time.sleep(1)
        self.parent.destroy()

    def restoreform(self):
        self.parent.withdraw()
        master = Toplevel()
        gr = GuiRestore(master)
        gr.parent.wait_window()
        self.parent.deiconify()
        del gr
    
#     def readme(self):
#         fh = open(os.path.join(dir_name,'docs', 'README.rst'), 'rb')
#         txt = fh.read().decode()
#         fh.close()
#         self.tex['state'] = NORMAL
#         self.tex.delete('1.0', END )
#         self.tex.insert(2.0,'\n\n' + txt)
#         self.tex['state'] = DISABLED
     

def showlicense():

    copyrightfile =  dir_name + os.sep +'docs/gpl-3.0.txt'

    root04 = Toplevel()
    root04.title(_('License...'))
    root04.resizable(0, 0)
    try:
        root04.attributes("-toolwindow", 1)
    except:
        root04.overrideredirect(1)

    def keyenter(event):
        root04.destroy()

    fh = open(copyrightfile, 'r')
    msg = fh.read()
    fh.close()

    kentrikoframe = ttk.Frame(root04)
    kentrikoframe.grid(column=0, row=0, sticky=(N, W, S, E))
    kentrikoframe.columnconfigure(0, weight=1)
    kentrikoframe.rowconfigure(0, weight=1)

    t=  ScrolledText(kentrikoframe, height=38, width=75, bg='#d9d9d9', relief=FLAT)
    t.grid(column=0, row=0, sticky=(N,S,W,E))
    t.insert(1.0, msg)
#     t.insert(END, '\n')
    t.configure(state=DISABLED)


    koumpi=ttk.Button(kentrikoframe, text=_('Close'), command=root04.destroy)
    koumpi.grid(column =0, row=1, sticky=E)
    koumpi.bind('<Return>', keyenter)

    for child in kentrikoframe.winfo_children():
        child.grid_configure(padx=2, pady=2)

    root04.update_idletasks()
    screen_width=root04.winfo_screenwidth()
    screen_hight=root04.winfo_screenheight()
    w = root04.winfo_width()
    h = root04.winfo_height()
    root04.geometry("%dx%d%+d%+d" % (w, h, (screen_width-w)/2, (screen_hight-h)/2))
    root04.grab_set()
    root04.focus_set()
    koumpi.focus()

class GuiRestore(GuiBackup):
    def __init__(self, parent=None, title=_('tkbak Restore Backup Files')):
        self.parent = parent
        self.title = title
        self.parent.title = self.title
        self.create_icon(self.parent)
        self.lis = []
        self.minima = StringVar()
        self.sxolio = StringVar()
        self.makewidgets()
        self.parent.update_idletasks()
        self.center_window(self.parent)
        self.parent.protocol("WM_DELETE_WINDOW", lambda: '')


    def makewidgets(self):
        frm = ttk.Frame(self.parent)
        frm.grid(row=0, column=0, sticky=ALL)
        #frm.config(bg='black')

        lblcomment = ttk.Label(frm, textvariable=self.sxolio)
        lblcomment.grid(row=0, column=0, columnspan=3, sticky=W+E)
        lstboxfromzip = Listbox(frm, width=50, height=24)
        lstboxfromzip.grid(row=1, column=0, sticky=ALL)
        lstboxfromzip.bind('<Double-1>', self.OnDouble)
        self.lstboxfromzip = lstboxfromzip
        vscbar = ttk.Scrollbar(frm, orient="vertical", command=self.lstboxfromzip.yview)
        self.lstboxfromzip.configure(yscrollcommand=vscbar.set)
        vscbar.grid(row=1, column=0, sticky=E+N+S)
        lstboxtorestore = Listbox(frm, width=50, height=24)
        lstboxtorestore.grid(row=1, column=1, sticky=ALL)
        self.lstboxtorestore = lstboxtorestore
        vscbar01 = ttk.Scrollbar(frm, orient="vertical", command=self.lstboxtorestore.yview)
        self.lstboxtorestore.configure(yscrollcommand=vscbar01.set)
        vscbar01.grid(row=1, column=1, sticky=E+N+S)
        ent = ttk.Entry(frm, width=30)
        ent.grid(row=2, column=0,  sticky=W)
        self.ent = ent

        btnepanaforaolon = ttk.Button(frm, text=_('All...'), state=DISABLED, command=self.movetorestore)
        btnepanaforaolon.grid(row=2, column=0, sticky=E)
        self.btnepanaforaolon = btnepanaforaolon

#         lblminima = ttk.Label(frm, textvariable=self.minima, width=30)
#         lblminima.grid(row=2, column=1, sticky=ALL)
#         self.lblminima = lblminima
        tex = ScrolledText(frm, width=50, height=3)
        tex.grid(row=2, column=1, sticky=ALL)
        self.tex = tex

        btnfindzip = ttk.Button(frm, text=_('Load zipped file'), command= self.openthezip)
        btnfindzip.grid(row=3, column=0)
        self.btnfindzip = btnfindzip

        btnextract = ttk.Button(frm, state=DISABLED, text= _('Deflating'), command=self.extractfromzip)
        btnextract.grid(row=3, column=1)
        self.btnextract = btnextract

        btncloseme = ttk.Button(frm, text=_('Close'), command=self.parent.destroy)
        btncloseme.grid(row=3, column=1, sticky=E)
        self.parent.update_idletasks()

        for child in frm.winfo_children():
            child.grid_configure(pady=5, padx=5)


    def loadme(self, getthefile):
        #file = r'C:\Users\Konstas\zip.zip'
        if zipfile.is_zipfile(getthefile):
            myzip = zipfile.ZipFile(getthefile, 'r')

            for f in myzip.namelist():
                self.lstboxfromzip.insert(END, f)

            self.lstboxfromzip.select_set(0)
    #         self.myzip = myzip

            if len(myzip.comment) > 0:
                self.sxolio.set(myzip.comment.decode())
            #    for file in self.lis:
            #        print(file)
        elif tarfile.is_tarfile(getthefile):
            myzip = tarfile.open(getthefile, 'r')

            for f in myzip.getnames():
                self.lstboxfromzip.insert(END, f)

            self.lstboxfromzip.select_set(0)

        myzip.close()
        self.btnfindzip['state'] = DISABLED

    def movetorestore(self):
        for item in self.lstboxfromzip.get(0, END):

            self.lstboxfromzip.select_set(0)
            selection = self.lstboxfromzip.curselection()

            self.lstboxtorestore.insert(END, item)
            self.lis.append(item)

            self.lstboxfromzip.delete(selection[0])
            self.btnextract['state'] = NORMAL

    def OnDouble(self, event):
        widget = event.widget
        selection=widget.curselection()
        val = widget.get(selection[0])
        self.lstboxtorestore.insert(END, val)
        self.lis.append(val)
        widget.delete(selection[0])
        self.btnextract['state'] = NORMAL

    def openthezip(self):
        ft = [('ZIP', '.zip'),
              ('Tar.gz', 'tar.gz'),
              ('All Files', '*')]

        p = askopenfilename(parent=self.parent, initialdir=os.path.expanduser('~'), \
                              title=self.title, filetypes=ft)
        p = os.path.normpath(p)
        self.ent.delete(0, END)
        self.ent.insert(0, p)
        self.loadme(self.ent.get())
        self.btnepanaforaolon['state'] = NORMAL

    def extractfromzip(self):
        sys.stdout = self
        extractdir = askdirectory(title=self.title)
        if askyesno(self.title, message= _('Restore to directory: {0}?').format(extractdir)) == True:
            backup.Restore(self.ent.get(), self.lis, extractdir)
            sys.stdout = sys.__stdout__
#             for file in self.lis:
#                 msg = _('Αποσυμπιέζω το: {0}').format(file)
#                 self.minima.set(msg)
#                 print(msg)
#                 self.myzip.extract(file, extractdir)
#         self.minima.set(self.myzip.comment.decode())
#         print(self.myzip.comment.decode())
#         self.myzip.close()
        self.btnextract['state'] = DISABLED


def run():
    root = Tk()
    GuiBackup(root)
    root.mainloop()
    
        
if __name__=='__main__':
    run()
