#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Created on 18-11-2013
Updated on 04-05-2014
@ author: Konstas Marmatakis
'''

import os
import sys
from distutils.core import setup
# from distutils.file_util import copy_file

if (sys.version_info.major, sys.version_info.minor) < (3, 2):
    print("You must have version 3.2 and above.")
    sys.exit(1)


files = ['docs/*', 'locale/*/LC_MESSAGES/*']
dat_files = []


if os.name == 'posix':
    ins_dir = '/usr/local/bin'
    try:
        if os.path.exists(os.path.join('/usr/bin', 'tkbak')):
            ins_dir = '/usr/bin'
            
        elif os.path.exists(os.path.join('/usr/local/bin', 'tkbak')):
            ins_dir = '/usr/local/bin'
    except:
        pass
    
    txt ='#!/usr/bin/env xdg-open\n\n[Desktop Entry]\nVersion=1.0\nType=Application\nTerminal=false\nName[el_GR]=TkBak\nExec={0}\nIcon={1}\nComment[el_GR]=Εφαρμογή για την δημιουργία και συμπίεση εφεδρικών αντιγράφων.\nComment=Application for zip and archive files and directories.\nName=TkBak\nGenericName[el_GR]=TkBak\nCategories=Utility\nTerminal=false\nStartupNotify=false\n'
    fh = open('tkbak.desktop', 'w')
    fh.write(txt.format(os.path.join(ins_dir, 'tkbak'), os.path.join('/usr/share/icons/hicolor/48x48/apps', 'tkbak.png')))
    fh.close()
    dat_files = [('/usr/share/icons/hicolor/48x48/apps', ['backup/docs/tkbak.png']),
                 ('/usr/share/applications', ['tkbak.desktop'])]
    
setup(name='tkbak',
      version=open('backup/docs/VERSION').read().strip(),
      description='Simple Backup Application',
      author='Konstas Marmatakis',
      author_email='marmako@gmail.com',
      url='https://bitbucket.org/kamar/tkbak',
      packages=['backup'],
      scripts=['tkbak', 'cr_shortcut.py'],
      package_data = {'backup': files},
      data_files = dat_files,
      license='GNU/GPLv3',
      keywords=['Utility', 'Backup'],
#       data_files=[('docs', ['docs/gpl-3.0.txt', 'AUTHORS', 'README.rst', 'TRANSLATORS', 'VERSION']),
#                   ('images', ['docs/gplv3-127x51.gif', 'docs/gplv3-127x51.png',
#                               'docs/gplv3-88x31.gif', 'docs/gplv3-88x31.png', 
#                               'docs/tkbak.gif', 'docs/tkbak.png'])],
      long_description=open('backup/docs/README.rst', encoding='utf-8').read().replace('\ufeff', ''),
      platforms=['Linux', 'Windows'],
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Environment :: X11 Applications',
                   'Intended Audience :: Other Audience',
                   'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                   'Operating System :: Microsoft',
                   'Operating System :: Microsoft :: Windows :: Windows 7',
                   'Operating System :: POSIX',
                   'Operating System :: POSIX :: Linux',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.2',
                   'Programming Language :: Python :: 3.3',
                   'Programming Language :: Python :: 3.4',
                   'Topic :: Desktop Environment',
                   'Topic :: System :: Archiving :: Backup'])

# if sys.argv[1] == 'install':
#     if os.name == 'posix':
#         ins_dir = ''
#         try:
#             if os.path.exists(os.path.join('/usr/bin', 'tkbak')):
#                 ins_dir = '/usr/bin'
#             elif os.path.exists(os.path.join('/usr/local/bin', 'tkbak')):
#                 ins_dir = '/usr/local/bin'
#         except:
#             pass
# #         try:
# #             locations = open('RECORD', encoding='utf-8').read()
# #             # print(locations)
# #             for line in locations.splitlines():
# #                 if line[-5:] == 'tkbak':
# #                     executable = line
# #         except:
# #             print('Can\'t read the location from the script.')                            
# #             locations='/usr/bin'
#     
#         txt ='#!/usr/bin/env xdg-open\n\n[Desktop Entry]\nVersion=1.0\nType=Application\nTerminal=false\nName[el_GR]=TkBak\nExec={0}\nIcon={1}\nComment[el_GR]=Εφαρμογή για την δημιουργία και συμπίεση εφεδρικών αντιγράφων.\nComment=Application for zip and archive files and directories.\nName=TkBak\nGenericName[el_GR]=TkBak\nCategories=Utility\nTerminal=false\nStartupNotify=false\n'
#         # copy_file('tkbak.desktop', '/usr/share/applications/')
#         copy_file('backup/docs/tkbak.png', '/usr/share/icons/hicolor/48x48/apps/')
#         try:
#             print('Writing {0} ...'.format(os.path.join('/usr/share/applications', 'tkbak.desktop')))
#             fh = open(os.path.join('/usr/share/applications/', 'tkbak.desktop'), 'w', encoding='utf-8')
#             fh.write(txt.format(os.path.join(ins_dir, 'tkbak'), os.path.join('/usr/share/icons/hicolor/48x48/apps', 'tkbak.png')))
#             fh.close()
#         except:
#             print('Error. Can\'t create {0}'.format(os.path.join('/usr/share/applications/', 'tkbak.desktop')))
#         finally:
#             fh.close()
# 
#     elif sys.argv[1] in ["uninstall", "remove"]:
#         png_loc = os.path.join('/usr/share/icons/hicolor/48x48/apps/', 'tkbak.png')
#         shortcut_loc = os.path.join('/usr/share/applications/', 'tkbak.desktop')
#         
#         if os.path.exists(png_loc):
#             print("Removing {0}...".format(png_loc))
#             os.unlink(png_loc)
#         
#         if os.path.exists(shortcut_loc):
#             print("Removing {0}...".format(shortcut_loc))
#             os.unlink(shortcut_loc)
#         
