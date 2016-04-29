import shutil
import os
import re

EPICS_KITS_DIR = "\\\\isis\\inst$\\Kits$\\CompGroup\\ICP\\EPICS\\EPICS_win7_x64"
GUI_KITS_DIR = "\\\\isis\\inst$\\Kits$\\CompGroup\\ICP\\Client"

# Find the latest version of EPICS
version = 0
folder = None
for x in os.listdir(EPICS_KITS_DIR):
    if os.path.isdir(os.path.join(EPICS_KITS_DIR, x)):
        m = re.match("BUILD-(\d+)", x)
        if m is not None:
            d = int(m.groups()[0])
            if d > version:
                version = d
                folder = x

print "Copying EPICS from %s, please wait..." % folder

shutil.copytree("%s\\%s" % (EPICS_KITS_DIR, folder), "C:\\Instrument\\Apps\\EPICS")

# Find the latest version of the GUI
version = 0
folder = None
for x in os.listdir(GUI_KITS_DIR):
    if os.path.isdir(os.path.join(GUI_KITS_DIR, x)):
        m = re.match("BUILD(\d+)", x)
        if m is not None:
            d = int(m.groups()[0])
            if d > version:
                version = d
                folder = x
                
print "Copying GUI from %s, please wait..." % folder

shutil.copytree("%s\\%s" % (GUI_KITS_DIR, folder), "ibex_gui")