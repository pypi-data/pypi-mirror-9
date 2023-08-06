#!/usr/bin/env python3
# encoding: utf-8
'''
backup -- Creates the zip files and backup.

Command line script for backup and ziping files.

@author:     K. Marmatakis

@copyright:  2015 All rights reserved.

@license:   GNU/GPL v3

@contact:   <marmako@gmail.com> 

'''

import os
import zipfile
import tarfile
import gettext
import locale
import time
import sys
import logging


glossa = locale.getdefaultlocale()[0]

dir_name = os.path.dirname(__file__)

t = gettext.translation("tkbak", localedir=dir_name + os.sep + "locale", codeset='utf-8', fallback=True, \
                        languages=[glossa])
_ = t.gettext
t.install()

def rename_old_path(old, new):
    """
    Renames the old tkbackup files and directories
    to tkbak. It doesn't deletes the files.
    """
    
    if os.path.exists(os.path.normpath(old)):
        if os.path.exists(os.path.join(old, '.tkbackup.log')):
            os.rename(os.path.join(old, '.tkbackup.log'), os.path.join(old, '.tkbak.log'))
            os.rename(old, new)
            
def create_dirs():
    
    if sys.platform.startswith('win') or sys.platform.endswith('NT'):
        rename_old_path(os.path.join(os.environ['APPDATA'], '.tkbackup'), os.path.join(os.environ['APPDATA'], '.tkbak'))
        if os.path.exists(os.path.normpath(os.path.join(os.environ['APPDATA'], '.tkbak'))):
            the_path = os.path.normpath(os.path.join(os.environ['APPDATA'], '.tkbak'))
    else:
        rename_old_path(os.path.join(os.path.expanduser('~'), '.tkbackup'), os.path.join(os.path.expanduser('~'), '.tkbak'))
        the_path = os.path.normpath(os.path.join(os.path.expanduser('~'), '.tkbak'))
    
    if not os.path.exists(the_path):
        os.mkdir(the_path)
    return the_path


logdir = create_dirs()
logger = logging.getLogger('tkbak Application')
logger.setLevel(logging.INFO)
log_file = os.path.join(logdir, '.tkbak.log')
fh = logging.FileHandler(log_file, encoding='utf-8')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
schand = logging.StreamHandler(sys.stdout)
schand.setLevel(logging.INFO)
schand.setFormatter(formatter)
logger.addHandler(schand)



def Backup(filesdirs=['dir'], target='zip_pyx.zip', ftype='typezip', mode='w', addcom=''):
    """Function that creats compressed files zip or tar.
    USAGE:
            Backup(filesdirs, target, ftype, mode, addcom)
    PARAMETERS:
            filesdirs: A list with the directories or files to be compressed.
            target: The full path and file name for the compressed file.
            ftype: The compressed file type. Possible arguments, 'typezip' or 'typetar'.
            mode: w for write, a for append, r for read.
            addcom: The comment for the zipfile. No comments allowed for tar."""

    count = 0
    target = target
    cdirs = set(filesdirs) # Removes duplicates.

    if ftype == 'typezip':

        zip_command = zipfile.ZipFile(target, mode, compression=zipfile.ZIP_DEFLATED)

        if len(addcom) > 0:
#             print(len(addcom))
            messagelog(_('Writing the comment: {0}').format(addcom))
            zip_command.comment = addcom.encode()
#             messagelog(zip_command.comment.decode())
        if len(filesdirs) == 0:
            messagelog(_('No files or directories for compressing.'))
            zip_command.close()
        
        for cdir in cdirs:
            if os.path.isdir(cdir):
                for rt, dirs, files in os.walk(cdir):
                    for file in files:

                        try:
                            minima = _('Compressing: ...{0}{1}').format(os.sep, file)
                            messagelog(minima)
                            folder = os.path.join(rt, file)
                            folder = folder.replace(os.path.expanduser('~'), "")
                            zip_command.write(os.path.join(rt, file), arcname=folder)
                            count += 1
                        except:
                            minima = _('Failled to compress {0}').format(file)
                            messagelog(minima)
                            pass

            elif os.path.isfile(cdir):
                try:
                    minima = _('Compressing: ...{0}').format(os.path.normpath(cdir))
                    messagelog(minima)
                    folder = os.path.normpath(cdir)
                    folder = folder.replace(os.path.expanduser('~'), "")

                    zip_command.write(os.path.normpath(cdir), arcname=folder)
                    count += 1
                except:
                    minima = _('Failled to compress {0}').format(os.path.normpath(cdir))
                    messagelog(minima)
                    pass
#         zip_command.close()

    elif ftype == 'typetar':
        mode = mode + ':gz'
        zip_command = tarfile.open(target, mode, encoding="utf-8")

        if len(addcom) > 0:
            messagelog(_('There is not support for comments.'))

        for cdir in cdirs:
            if os.path.isdir(cdir):
                for rt, dirs, files in os.walk(cdir):
                    for file in files:

                        try:
                            minima = _('Compressing: ...{0}{1}').format(os.sep, file)
                            messagelog(minima)
                            folder = os.path.join(rt, file)
                            folder = folder.replace(os.path.expanduser('~'), "")
                            zip_command.add(os.path.join(rt, file), arcname=folder)
                            count += 1
                        except:
                            minima = _('Failled to compress {0}').format(file)
                            messagelog(minima)
                            pass

            elif os.path.isfile(cdir):
                try:
                    minima = _('Compressing: ...{0}').format(os.path.normpath(cdir))
                    messagelog(minima)
                    folder = os.path.normpath(cdir)
                    folder = folder.replace(os.path.expanduser('~'), "")

                    zip_command.add(os.path.normpath(cdir), arcname=folder)
                    count += 1
                except:
                    minima = _('Failled to compress {0}').format(os.path.normpath(cdir))
                    messagelog(minima)
                    pass
    messagelog(_('The file {0} is compressed').format(target))
    zip_command.close()

    minima = _('The file: {0} is created {1}').format(os.path.normpath(target), '\n')
    messagelog(minima)

    minima = _('Compressed total {0} files.{1}').format(count, '\n')
    messagelog(minima)

def Restore(ziportar='', files=[], todirectory='.'):
    count = 0
    if zipfile.is_zipfile(ziportar) == True:
        messagelog(_('The file type of {0} is zip').format(ziportar))
        time.sleep(3)
        myzipfile = zipfile.ZipFile(ziportar, 'r')
        for file in files:
            msg = _('Decompressing: {0}').format(file)
            messagelog(msg)
            myzipfile.extract(file, todirectory)
            count += 1
        myzipfile.close()
    elif tarfile.is_tarfile(ziportar) == True:
        messagelog(_('The type file of {0} is tar').format(ziportar))
        time.sleep(3)
        myzipfile = tarfile.open(ziportar)
        for file in files:
            msg = _('Decompressing: {0}').format(file)
            messagelog(msg)
            myzipfile.extract(file, todirectory)
            count += 1
        myzipfile.close()
    else:
        messagelog(_('The file type of {0} is not supported.').format(ziportar))

    messagelog(_('Decompressed total {0} files from the file {1}.').format(count, ziportar))


def messagelog(msg):
    print(msg)
    logger.info(msg)
    
    

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", help="Backups selected files and directories.")
    parser.add_argument("-r", help="Restores from compressed file.")
    
