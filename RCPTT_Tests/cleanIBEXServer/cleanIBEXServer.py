"""
Script to clean up files in the IBEX server between tests
"""
import os

import stat
import subprocess
import shutil
from subprocess import PIPE
from time import sleep

import errno
import psutil


# How often should be clean the directories
RUN_CLEAN_PER = 0

# Path to the console process
PATH_TO_CONSOLE_EXE = "C:/Instrument/Apps/EPICS/tools/master/cygwin_bin/console"

# Path to DAE Data directory
PATH_TO_DAE_DATA = os.path.join("C:\\", "data")

# default config path
default_configs_path = os.path.join("C:\\", "Instrument", "Settings", "config",
                                    os.environ.get("COMPUTERNAME", "NAME"), "configurations")

# path to ICP CONFIG ROOT
PATH_TO_ICPCONFIGROOT = os.environ.get("ICPCONFIGROOT", default_configs_path)

# path to the clean ibex script and resources
CLEAN_IBEX_DIR = os.path.dirname(os.path.realpath(__file__))

# name of the file representing the "last config" to be copied
LAST_CONFIG_FILE = "last_config.txt"

# names of DAE tables
WIRING_TABLE = "RCPTT_wiring128.dat"
SPECTRA_TABLE = "RCPTT_spectra128.dat"
DETECTOR_TABLE = "RCPTT_detector128.dat"

# name of the blank config
BLANK_CONFIG_DIR = "rcptt_blank"

# log file for exception logging
LOG_FILE = os.path.join(CLEAN_IBEX_DIR, "cleanIBEXServer.log")

#ASCII character for an Enquiry (i.e. CTRL+E)
ENQ_SIGNAL = "\x05"

# ASCII character for Device Control 4 (i.e. CTRL+T)
DC4_SIGNAL = "\x14"

#ASCII character for Cancel (i.e. CTRL+X)
CAN_SIGNAL = "\x18"

# Signal to exit a console
EXIT_CONSOLE_SIGNAL = ENQ_SIGNAL + "c."

# Block server process name
BLOCKSERVER = "BLOCKSVR"

# DAE process name
DAE = "ISISDAE_01"



def remove_test_dir_and_files(root_path):
    """
    Remove all directories and files which start with rcptt_
    :param root_path: path to search through
    :return:
    """
    if not os.path.exists(root_path):
        print("Path for this doesn't exist")
        return
    for path in os.listdir(root_path):
        if path.startswith("rcptt_"):
            print "  {0}".format(path)
            path_to_del = os.path.join(root_path, path)
            if os.path.isdir(path_to_del):
                shutil.rmtree(os.path.join(root_path, path))
            else:
                os.remove(path_to_del)


def set_default_config(config_path):
    """
    Copy files to create a default configuration
    :param config_path:
    :return:
    """
    shutil.copytree(os.path.join(CLEAN_IBEX_DIR, BLANK_CONFIG_DIR),
                    os.path.join(config_path, BLANK_CONFIG_DIR))

    shutil.copyfile(os.path.join(CLEAN_IBEX_DIR, LAST_CONFIG_FILE),
                    os.path.join(PATH_TO_ICPCONFIGROOT, LAST_CONFIG_FILE))

def check_dir_exists(path):
    """
    Check a directory exists, and create it if it does not
    :param path: the directory path
    :return:
    """
    if not os.path.exists(path):
        os.makedirs(path)

def copy_dae_tables():
    """
    Copy DAE tables from system test folder to a predefined 
    location on the machine
    :return:
    """
    table_source = os.path.join(CLEAN_IBEX_DIR, "Tables")
    
    table_dest = os.path.join(PATH_TO_ICPCONFIGROOT, "tables")
    check_dir_exists(table_dest)
    
    shutil.copyfile(os.path.join(table_source, WIRING_TABLE), os.path.join(table_dest, WIRING_TABLE))
    shutil.copyfile(os.path.join(table_source, SPECTRA_TABLE), os.path.join(table_dest, SPECTRA_TABLE))
    shutil.copyfile(os.path.join(table_source, DETECTOR_TABLE), os.path.join(table_dest, DETECTOR_TABLE))

def safe_execute(function_to_execute, error_no, *args):
    """
    Execute input command in a try catch. Stop script in case of error.
    :param function_to_execute: the command to execute
    :param error_no: the error number to use when quitting the script
    :param args: arguments to the command to execute
    :return:
    """
    try:
        function_to_execute(*args)
    except Exception as ex:
        _log_and_exit(ex, error_no)

def safe_set_default_config(configurations_path):
    try:
        set_default_config(configurations_path)
    except IOError:
        sleep(6)
        set_default_config(configurations_path)

def safe_copy_dae_tables():
    try:
        copy_dae_tables()
    except IOError:
        sleep(6)
        copy_dae_tables()

def reboot_dae(error_no):
    """
    Reboot the dae then immediately move the data directory
    :return:
    """
    for proc in psutil.process_iter():
        try:
            if proc.name() == "isisicp.exe":
                proc.kill()
                break
        except psutil.AccessDenied:
            pass

    # reboot the dae by stopping it (dae procServ is set to autorestart)
    stop_ioc(DAE, error_no)

def delete_dae_experiments_file(error_no):
    """
    Delete dae experiments file
    :param error_no:
    :return:
    """
    path_exists = os.path.exists(PATH_TO_DAE_DATA)
    os_error = None
    if path_exists:
        for i in range(2000):
            try:
                os.rename(PATH_TO_DAE_DATA, PATH_TO_DAE_DATA + "del")
                print "Data dir moved to datadel"
                path_exists = False
                break
            except OSError as e:
                os_error = e
                sleep(0.01)

    if path_exists:
        print "Can not delete data dir!"
        _log_and_exit("Can not delete data dir! " + e.strerror, error_no)

def reset_ibex_backend():
    """
    reset the ibex backend
    :return:
    """

    # stop the block server
    # procServ is set to autorestart the block server, so we need to toggle the autorestart flag first
    safe_execute(toggle_ioc_autorestart, 3, BLOCKSERVER, 4)
    safe_execute(stop_ioc, 5, BLOCKSERVER, 6)

    # delete test artefacts
    configurations_path = os.path.join(PATH_TO_ICPCONFIGROOT, "configurations")
    print "Removing test configurations in {0}".format(configurations_path)
    safe_execute(remove_test_dir_and_files, 7, configurations_path)

    components_path = os.path.join(PATH_TO_ICPCONFIGROOT, "components")
    print "Removing test components in {0}".format(components_path)
    safe_execute(remove_test_dir_and_files, 8, components_path)

    synoptics_path = os.path.join(PATH_TO_ICPCONFIGROOT, "synoptics")
    print "Removing test synoptics in {0}".format(synoptics_path)
    safe_execute(remove_test_dir_and_files, 9, synoptics_path)

    safe_execute(safe_set_default_config, 10, configurations_path)
    safe_execute(safe_copy_dae_tables, 11)
    safe_execute(_delete_data_del_dir, 12)

    # reboot the block server by restoring the autorestart flag
    safe_execute(toggle_ioc_autorestart, 13, BLOCKSERVER, 14)

    safe_execute(reboot_dae, 15, 16)
    safe_execute(delete_dae_experiments_file, 17, 18)
    safe_execute(_delete_data_del_dir, 19)
    print "Deleted the moved data dir"


def _log_and_exit(error, exit_code):
    """
    Log the error and exit
    :param error: error to log
    :param exit_code: error number to exit with
    :return:
    """
    with file(LOG_FILE, mode="a") as f:
        f.write("Error {0}: {1}\n".format(exit_code, error))

    print error

    exit(exit_code)


def _delete_data_del_dir():
    """
    Delete the old data to delete dir
    :return:
    """
    path_to_dae_data_del = PATH_TO_DAE_DATA + "del"
    if not os.path.exists(path_to_dae_data_del):
        return

    def error_remove_readonly(func, path, exc):
        """Delete readonly files on error in rmtree"""
        exc_value = exc[1]
        if func in (os.rmdir, os.remove) and exc_value.errno == errno.EACCES:
            # change the file to be readable,writable,executable: 0777
            os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            # retry
            func(path)
        else:
            raise
    try:
        shutil.rmtree(path_to_dae_data_del,onerror=error_remove_readonly)
    except OSError as ex:
        sleep(3)
        shutil.rmtree(path_to_dae_data_del,onerror=error_remove_readonly)


def stop_ioc(console_name, error_no):
    """
    Stop an ioc running in a console. ProcServ will automatically restart it if it is set to do so.
    :param console_name: name of the console
    :return:
    """
    _send_via_console(console_name, CAN_SIGNAL, error_no)
    print("Stopped or restarted the {0}".format(console_name))


def toggle_ioc_autorestart(console_name, error_no):
    """
    Toggle the procServ autorestart flag in a console
    :param console_name: name of the console
    :return:
    """
    _send_via_console(console_name, DC4_SIGNAL, error_no)
    print("Toggled autorestart for the {0}".format(console_name))


def _send_via_console(console_name, message, error_no):
    """
    Open a console in a subprocess
    :param console_name: name of the console
    :return: the subprocess
    """
    p = subprocess.Popen([PATH_TO_CONSOLE_EXE, "-M", "localhost", console_name],
                         stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, errors = p.communicate(message + EXIT_CONSOLE_SIGNAL)

    if errors:
        _log_and_exit(errors, error_no)

    missing_console_msg = "console '" + console_name + "' not found"
    if missing_console_msg in output:
        _log_and_exit(output, error_no)



def need_run_clean():
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
    if need_run_clean():
        reset_ibex_backend()
    _log_and_exit("success", 0)
