##
## This script is called without parameters
##
## It copies media files from an old SRP folder over to a Kofa
## instance media folder. It does not remove copied folders.
##
## Configuration is done below.
##
## At end a list of dirs that were copied or are empty is returned.
##
## Please note that for changing groups of files/directories, you
## normally have to be root. This script is therefore normally run with
## sudo.
##

## ######################################################################
## CONFIGURATION
##

## The folder where all source docs can be found
#SRC_DIR = "/zope/instances/aaue-images"
SRC_DIR = "/tmp/migration/src"

## The students folder in Kofa where files should go to
#DST_DIR = "/kofa/aaue/var/datacenter/media/students"
DST_DIR = "/tmp/migration/dst"

## The Ids of new students to search for in old portal.
NEW_IDS_CSV = "StudentIds.csv"

## The ids of students that will will get a complete new number, not
## an updated one. Must contain a mapping of old ids to new ids.
## If no such update should be performed, please set the constant to None.
ID_MAP_CSV = None
ID_MAP_CSV = "id_mapping.csv"

## Permissions to be set on new files/dirs. Set OWNER and/or GROUP to
## None to leave them unchanged after creation.
UMASK = 0664
OWNER = 'uli'
GROUP = 'nogroup'

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

def new_folder_name(stud_id):
    # compute new folder name from stud_id (old stud_ids only)
    num = int(stud_id[1:])
    num = num / 10000 * 10
    return '%05d' % num

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

def copy_file(file_src, file_dst):
    create_path(os.path.dirname(file_dst))
    print "COPY FILE: %s -> %s" % (file_src, file_dst)
    shutil.copyfile(file_src, file_dst)
    set_perms(file_dst)
    return

def get_new_old_id_mapping():
    """Returns a dict mapping from _new_ ids to old (SRP) ids.

    The dict is read from ID_MAP_CSV file. If this var is set to
    ``None`` an empty dict is returned. The ID_MAP_CSV contains only
    the student ids of those students, for which the standard method
    (new_id=CHAR+old_id) does not work.
    """
    if ID_MAP_CSV is None:
        return {}
    if not os.path.isfile(ID_MAP_CSV):
        raise IOError(
            "No such file for mapping new to old ids: %s" % ID_MAP_CSV)
    result = dict()
    reader = csv.DictReader(open(ID_MAP_CSV, 'rb'))
    for row in reader:
        result[row['new_id']] = row['student_id']
    return result

# special ids not handled in common way
new_to_old_map = get_new_old_id_mapping()
removable_dirs = []
reader = csv.DictReader(open(NEW_IDS_CSV, 'rb'))
for row in reader:
    new_stud_id = row['student_id']
    stud_id = new_to_old_map.get(new_stud_id[1:], new_stud_id[1:])
    src_folder = os.path.join(SRC_DIR, stud_id[0], stud_id)
    dst_folder = os.path.join(
        DST_DIR, new_folder_name(new_stud_id[1:]), new_stud_id)
    if not os.path.exists(src_folder):
        print "No old data for %s. Skipping." % stud_id
        continue
    if os.path.exists(dst_folder):
        print "Destination folder exists already: %s. Skipping" % (dst_folder)
        continue
    removable_dirs.append(src_folder)
    src_files = os.listdir(src_folder)
    if len(src_files) == 0:
        print "Empty source folder for %s. Skipping." % stud_id
        continue
    for name in src_files:
        file_src = os.path.join(src_folder, name)
        file_dst = os.path.join(dst_folder, name.replace(stud_id, new_stud_id))
        copy_file(file_src, file_dst)

print "DIRS TO REMOVE: "
for name in removable_dirs:
    print name
