import shutil
import os
import re
import sys

EPICS_KITS_DIR = "\\\\isis\\inst$\\Kits$\\CompGroup\\ICP\\EPICS\\EPICS_win7_x64"
GUI_KITS_DIR = "\\\\isis\\inst$\\Kits$\\CompGroup\\ICP\\Client"

EPICS_BUILD_FOLDER_PATTERN = "BUILD-(\d+)"

# Find the latest version of EPICS
version = 0
folder = None
for x in os.listdir(EPICS_KITS_DIR):
    m = re.match(EPICS_BUILD_FOLDER_PATTERN, x)
    if m is not None:
        if os.path.isfile(os.path.join(EPICS_KITS_DIR, x, 'EPICS', 'COPY_COMPLETE.txt')):
            d = int(m.groups()[0])
            if d > version:
                version = d
                folder = x
        else:
            print "Warning: COPY_COMPLETE not found for build " + m.groups()[0]
            print "This might be because the build is incomplete, or because the folder structure has changed."
			
			
if folder is not None: 
    print "Copying EPICS from %s, please wait..." % folder
    shutil.copytree("%s\\%s" % (EPICS_KITS_DIR, folder), "C:\\Instrument\\Apps\\EPICS")
else:
    print "Cannot find EPICS"
    sys.exit(1)

# Find the latest version of the GUI
version = 0
folder = None
for x in os.listdir(GUI_KITS_DIR):
    if os.path.isfile(os.path.join(GUI_KITS_DIR, x, 'COPY_COMPLETE.txt')):
        m = re.match("BUILD(\d+)", x)
        if m is not None:
            d = int(m.groups()[0])
            if d > version:
                version = d
                folder = x
                
if folder is not None: 
    print "Copying GUI from %s, please wait..." % folder
    shutil.copytree("%s\\%s" % (GUI_KITS_DIR, folder), "ibex_gui")
else:
    print "Cannot find GUI"
    sys.exit(1)
