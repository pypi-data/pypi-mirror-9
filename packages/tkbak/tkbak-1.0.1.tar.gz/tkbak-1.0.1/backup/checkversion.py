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
#===============================================================

import re
import os
import sys
import gettext
import locale
import urllib
import urllib.request

glossa = locale.getdefaultlocale()[0]

dir_name = os.path.dirname(__file__)

t = gettext.translation("tkbak", localedir=dir_name + os.sep + "locale", codeset='utf-8', fallback=True, \
                        languages=[glossa])
_ = t.gettext
t.install()


def check_version():
    """
    Checks for new version in 'https://testpypi.python.org/pypi/tkbak/'
    and returns the version number if there greater than local version.
    """
    
    dir_name = os.path.dirname(__file__)
    try:
        response = urllib.request.urlopen('https://testpypi.python.org/pypi/tkbak/')
        html = response.read()
    except urllib.error.URLError:
#        print("No connection")
        return None

    pat = "tkbak (\d+\.\d+\.\d+)"
    m = re.compile(pat)
    mobj = m.search(html.decode())

    ver = open(os.path.join(dir_name,'docs', 'VERSION')).read().strip()
#     print('Running version: {0}\nInternet version: {1}'.format( ver, mobj.group(1)))
    if ver < mobj.group(1):
        return mobj.group(1)

def download_me(*the_urls, block_size=8192):
    """Downloads a file from a site.
USAGE: python3 downloadme.py http://1 http://2 ...
Author: Konstas Marmatakis <marmako[at]gmail[dot]com>
License: GNU/GPL v 3.0

    """
    
    for the_url in the_urls:
        the_url = urllib.parse.unquote(the_url)
        site = urllib.request.urlopen(the_url)
        r = site.info()
        #file_name = the_url.split('/)[-1:]
        #print(len(site.read()))
        file_size = int(r.get('Content-Length'))
#         site.seek(0)
        
        file_name = the_url.split('/')[-1:][0] 
        file_seek = 0
        
        if os.path.exists(file_name):
            localfile = open(file_name, 'rb')
            content = localfile.read()
            localfile.close()
            
            if len(content) == file_size:
                print(_('The file allready exists.'))
                return None
        
##        print('Κατεβάζω το αρχείο {0}.\n'.format(os.path.abspath(localfile)))
        print(_("Downloading: {0}\nBytes: {1} KBytes: {2:.2f}").format(os.path.abspath(file_name),\
                file_size, int(file_size/1024)))

        try:
            if file_size <= block_size:
                fh = open(file_name, 'wb')
                megethos_arxeiou_kt = file_size
                fh.write(site.read())
            else:
                fh = open(file_name, 'wb')
                megethos_arxeiou_kt = 0

                while True:
#                     site.read(file_seek)
                    buffer = site.read(block_size)
                    if not buffer:
                        break
    
                    megethos_arxeiou_kt += len(buffer)
                    fh.write(buffer)
                    
                    prcnt = (megethos_arxeiou_kt / file_size)
                    
                    katastasi = "{0:>6,d}kb {1:.2%}".format(round(megethos_arxeiou_kt/1024),\
                                                            prcnt)
                    katastasi = katastasi + " " + "=" * int(prcnt * 100 / 2) + ">"
                    print(_("Downloaded: {0}").format(katastasi))
#                     sys.stdout.write("\rΚατέβηκαν: " + katastasi)
#                     sys.stdout.flush()
#  
#             sys.stdout.write("\n")
            print()
            print(_("Downloading completed."))
        finally:
            fh.close()

def downloadthefile(ver):
    """
    Downloads the newest version.
    """
    try:
        filen = 'https://testpypi.python.org/packages/source/t/tkbak/tkbak-{0}.tar.gz'.format(ver)
        download_me(filen)
    except:
        print(_("Cannot download: {0}").format(filen))
        try:
            filen  = 'https://testpypi.python.org/packages/source/t/tkbak/tkbak-{0}.zip'.format(ver)
            print(_("Trying: {0}").format(filen))
            download_me(filen)
        except:
            print(_("Cannot download: {0}").format(filen))
             
if __name__ == '__main__':
    download_me('https://testpypi.python.org/packages/source/t/tkbak/tkbak-{0}.tar.gz'.format(check_version()))
    #print(check_version())
    
