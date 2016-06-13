

import os
import subprocess
import shutil
from subprocess import PIPE
from time import sleep

# How often should be clean the directories
RUN_CLEAN_PER = 0

# Path to the console process
PATH_TO_CONSOLE_EXE = "C:/Instrument/Apps/EPICS/tools/master/cygwin_bin/console"

# Path to DAE Data directory
PATH_TO_DAE_DATA = os.path.join("C:\\", "data")

# default config path
default_configs_path = os.path.join("C:\\", "Instrument", "Settings", "config", os.environ.get("COMPUTERNAME", "NAME"), "configurations")

# path to ICP CONFIG ROOT
PATH_TO_ICPCONFIGROOT = os.environ.get("ICPCONFIGROOT", default_configs_path)


def remove_test_dirs(root_path):
    """
    Remove all directories which start with rcptt
    :param root_path: path to search through
    :return:
    """
    if not os.path.exists(root_path):
        print("Path for this doesn't exist")
        return
    for path in os.listdir(root_path):
        if path.startswith("rcptt"):
            print "  {0}".format(path)
            shutil.rmtree(os.path.join(root_path, path))


def reset_ibex_backend():
    """
    reset the ibex backend
    :return:
    """

    configurations_path = os.path.join(PATH_TO_ICPCONFIGROOT, "configurations")
    print "Removing test configurations in {0}".format(configurations_path)
    remove_test_dirs(configurations_path)

    components_path = os.path.join(PATH_TO_ICPCONFIGROOT, "components")
    print "Removing test components in {0}".format(components_path)
    remove_test_dirs(components_path)

    synoptics_path = os.path.join(PATH_TO_ICPCONFIGROOT, "synoptics")
    print "Removing test synoptics in {0}".format(synoptics_path)
    remove_test_dirs(synoptics_path)

    # reboot the block server
    restart_ioc_in_console("BLOCKSVR")

    # reboot the dae then immediately move the data directory
    restart_ioc_in_console("ISISDAE_01")

    # delete dae experiments file
    success = False
    for i in range(200):
        try:
            os.rename(PATH_TO_DAE_DATA, PATH_TO_DAE_DATA + "del")
            success = True
            break
        except OSError as ex:
            sleep(0.01)

    if not success:
        print "Can not delete data dir!"
        exit(2)

    shutil.rmtree(PATH_TO_DAE_DATA + "del")


def restart_ioc_in_console(console_name):
    """
    Restart an ioc running in a console
    :param console_name: name of the console
    :return:
    """

    p = subprocess.Popen([PATH_TO_CONSOLE_EXE, "-M", "localhost", console_name],
                         stdin=PIPE, stdout=PIPE, stderr=PIPE)
    p.communicate(chr(24) + chr(5) + "c.")
    print("Restarted the {0}".format(console_name))


def run_clean():
    """
    Should we run a clean, only run a clean every RUN_CLEAN_PER tests
    :return:true if clean; false otherwise
    """
    test_run_num = os.path.join(PATH_TO_DAE_DATA, "test_run_num.txt")
    try:
        last = "0"
        for line in file(test_run_num):
            if line.strip() != "":
                last = line.strip()
        run = int(last)
    except (IOError, ValueError):
        run = 0
    run += 1
    if run > RUN_CLEAN_PER:
        return True
    print("Run {0} (cleans at {1})".format(run, RUN_CLEAN_PER))
    try:
        with file(test_run_num, mode="a") as f:
            f.write("{0}\n".format(run))
        return False
    except IOError:
        print("Could not write run number")
        return False

if __name__ == "__main__":
    if run_clean():
        reset_ibex_backend()
