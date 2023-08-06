#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Only for windows"""

import os
import sys
import distutils.sysconfig


python_exe = os.path.join(distutils.sysconfig.EXEC_PREFIX, "pythonw.exe")

def create_app_shortcut(directory, filename, app):
    filename = os.path.normpath(os.path.join(directory, filename + ".lnk"))
    icon = os.path.normpath(os.path.join(distutils.sysconfig.get_python_lib(), 'backup', 'docs', 'tkbak.ico'))
    app = os.path.normpath(os.path.join(sys.prefix, "Scripts", app))
    create_shortcut(python_exe, "tkbak Simple Backup and Restore Application.", filename, app, "", icon)
    file_created(filename)


if sys.argv[1] == '-install' or sys.argv[1] == 'install':
    
    try:
        try:
            desktop = get_special_folder_path("CSIDL_COMMON_DESKTOPDIRECTORY")
            
        except OSError:
            desktop =  get_special_folder_path("CSIDL_DESKTOPDIRECTORY")
            
    except OSError:
        pass

    try:
        try:
            startmenu = get_special_folder_path("CSIDL_COMMON_PROGRAMS") #"CSIDL_COMMON_STARTMENU"
        except OSError:
             startmenu = get_special_folder_path("CSIDL_PROGRAMS")
    except OSError:
        pass

    create_app_shortcut(desktop, "TkBak", "tkbak")      
    create_app_shortcut(startmenu, "TkBak", "tkbak")

elif sys.argv[1] == '-remove':
    pass


    


