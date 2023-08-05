##
## This script is called without parameters.
##
## It moves fingerprint minutiae from a reload folder to their right place in
## the media folder.
##
## Configuration is done below.
##
##
## Please note that for changing groups of files/directories, you
## normally have to be root. This script is therefore normally run with
## sudo.
##

## ######################################################################
## CONFIGURATION
##

## The folder where all source docs can be found (can be any folder)
#SRC_DIR = "/kofa/uniben/var/datacenter/media/students/reload"
SRC_DIR = "/kofa/uniben_fpm"

## The students folder in Kofa where files should go to
DST_DIR = "/kofa/uniben/var/datacenter/media/students"


## Permissions to be set on new files/dirs. Set OWNER and/or GROUP to
## None to leave them unchanged after creation.
UMASK = 0664
OWNER = 'kofa'
GROUP = 'kofa'

##
## CONFIGURATION END
## ######################################################################

import csv
import os
import shutil
import sys
from grp import getgrnam
from pwd import getpwnam

OWNER_ID = OWNER and getpwnam(OWNER)[2] or -1
GRP_ID = GROUP and getgrnam(GROUP)[2] or -1
DIR_UMASK = UMASK | 0111  # directories need extra x-permission

def set_perms(path):
    # set permissions and ownership for path
    if os.path.isdir(path):
        os.chmod(path, DIR_UMASK)
    else:
        os.chmod(path, UMASK)
    os.chown(path, OWNER_ID, GRP_ID)
    return

def final_subfolder(stud_id):
    # compute new folder name from stud_id
    num = int(stud_id[1:])
    num = num / 1000
    return '%05d' % num

def copy_file(file_src, file_dst):
    print "COPY FILE: %s -> %s" % (file_src, file_dst)
    shutil.copyfile(file_src, file_dst)
    set_perms(file_dst)
    return

def create_path(path):
    # create path with subdirs, if it does not exist (completely)
    if os.path.exists(path):
        return
    parent = os.path.dirname(path)
    if not os.path.exists(parent):
        # create parent first
        create_path(parent)
    print "CREATE PATH ", path
    os.mkdir(path)
    set_perms(path)
    return

if not os.path.exists(SRC_DIR):
    sys.exit("No source folder %s. Skipping." % SRC_DIR)

if len(os.listdir(SRC_DIR)) == 0:
    sys.exit("Empty source folder for %s. Skipping." % SRC_DIR)

for stud_id in os.listdir(SRC_DIR):
    subfolder_name = final_subfolder(stud_id)
    dst_folder = os.path.join(DST_DIR, subfolder_name, stud_id)
    if not os.path.exists(dst_folder):
        #print "Destination folder does not exist: %s. Skipping" % (dst_folder)
        #continue
        create_path(dst_folder)

    src_subfolder = os.path.join(SRC_DIR, stud_id)
    for fingernumber in os.listdir(src_subfolder):
        src_file = os.path.join(SRC_DIR, src_subfolder, fingernumber)
        dst_file = os.path.join(DST_DIR, subfolder_name, stud_id,
            'finger%s_%s.fpm' % (fingernumber, stud_id))
        if os.path.exists(dst_file):
            print "Destination file exists: %s. Skipping" % (dst_file)
            continue
        copy_file(src_file, dst_file)
