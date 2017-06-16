"""
Script to clean up files in the IBEX server between tests

IMPORTANT: IF YOU UPDATE THIS FILE, IT MUST BE ALSO UPDATED
IN THE RCPTT CLEAN IBEX SERVER FILE CONTEXT
"""
import os

import stat
import subprocess
import shutil
from subprocess import PIPE
import time
from threading import Thread
from time import sleep
from datetime import datetime as dt

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

# names of TCB files
TCB1 = RCPTT_TCB_1.dat
TCB2 = RCPTT_TCB_2.dat

# name of experimental database rb number
EXP_DB_RBNUMBER_FILE = "experimental_database_rb_numbers.xml"

# name of the blank config
BLANK_CONFIG_DIR = "rcptt_blank"

# log file for exception logging
LOG_FILE = os.path.join(CLEAN_IBEX_DIR, "..", "cleanIBEXServer.log")

# ASCII character for an Enquiry (i.e. CTRL+E)
ENQ_SIGNAL = "\x05"

# ASCII character for Device Control 4 (i.e. CTRL+T)
DC4_SIGNAL = "\x14"

# ASCII character for Cancel (i.e. CTRL+X)
CAN_SIGNAL = "\x18"

# Signal to exit a console
EXIT_CONSOLE_SIGNAL = ENQ_SIGNAL + "c."

# Block server process name
BLOCKSERVER = "BLOCKSVR"

# DAE process name
DAE = "ISISDAE_01"

# Console name of Experiment database
EXPDB_CONSOLE_NAME = "EXPDB"

try:
    build_number = os.environ['BUILD_NUMBER']
except:
    build_number = dt.now().strftime("%y_%m_%d_%H_%M_%S")


# Error codes
class ErrNum(object):
    BS_TOGGLE_OFF = 3,
    BS_STOP = 4,
    DAE_TOGGLE_OFF = 5,
    DAE_STOP = 6,
    DELETE_DATA = 7,
    BS_TOGGLE_ON = 8,
    DAE_TOGGLE_ON = 9,
    RELOAD_RB_NUMBERS = 10


class SafeExErrNum(object):
    BS_TOGGLE_OFF = 10,
    BS_STOP = 11,
    DAE_TOGGLE_OFF = 12,
    DAE_STOP = 13,
    REMOVE_TEST_DIR = 14,
    REMOVE_TEST_DIR_2 = 15,
    REMOVE_TEST_DIR_3 = 16,
    SET_DEFAULT_CONFIG = 17,
    COPY_DAE = 18,
    DELETE_DATA = 19,
    DELETE_DATA_DEL = 20,
    DELETE_DATA_DEL_2 = 21,
    BS_TOGGLE_ON = 22,
    DAE_TOGGLE_ON = 23,
    RELOAD_RB_NUMBERS = 24,
    COPY_TCB = 25

    
class ReadLine(object):
    """
    Read a number of lines from the stdout of a process.
    """
    
    def __init__(self, p, count):
        """
        Init.
        
        :param p: process from which the stdout is read
        :param count: number of lines to read
        """
        self.last_line = ""
        self.p = p
        self.count = count

    def run(self):
        """
        Read the lines from stdout.
        """
        for i in range(self.count):
            self.last_line = self.p.stdout.readline()
            print "     console output {0}".format(self.last_line)


def remove_test_dir_and_files(root_path):
    """
    Remove all directories and files which start with rcptt_.
    
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
    Copy files to create a default configuration.
    
    :param config_path:
    :return:
    """
    shutil.copytree(os.path.join(CLEAN_IBEX_DIR, BLANK_CONFIG_DIR),
                    os.path.join(config_path, BLANK_CONFIG_DIR))

    shutil.copyfile(os.path.join(CLEAN_IBEX_DIR, LAST_CONFIG_FILE),
                    os.path.join(PATH_TO_ICPCONFIGROOT, LAST_CONFIG_FILE))


def check_dir_exists(path):
    """
    Check a directory exists, and create it if it does not.
    
    :param path: the directory path
    :return:
    """
    if not os.path.exists(path):
        os.makedirs(path)


def killproc(name):
    for proc in psutil.process_iter():
        try:
            if proc.name() == name:
                proc.kill()
                break
        except psutil.AccessDenied:
            pass


def copy_dae_tables():
    """
    Copy DAE tables from system test folder to a predefined
    location on the machine.
    
    :return:
    """
    table_source = os.path.join(CLEAN_IBEX_DIR, "Tables")
    
    table_dest = os.path.join(PATH_TO_ICPCONFIGROOT, "tables")
    check_dir_exists(table_dest)
    
    shutil.copyfile(os.path.join(table_source, WIRING_TABLE), os.path.join(table_dest, WIRING_TABLE))
    shutil.copyfile(os.path.join(table_source, SPECTRA_TABLE), os.path.join(table_dest, SPECTRA_TABLE))
    shutil.copyfile(os.path.join(table_source, DETECTOR_TABLE), os.path.join(table_dest, DETECTOR_TABLE))
    

def copy_tcb_files():
    """
    Copy TCB files from system test folder to a predefined 
    location on the machine.
    
    :return:
    """
    tcb_source = os.path.join(CLEAN_IBEX_DIR, "tcb")
    
    tcb_dest = os.path.join(PATH_TO_ICPCONFIGROOT, "tcb")
    check_dir_exists(tcb_dest)
    
    shutil.copyfile(os.path.join(tcb_source, TCB1), os.path.join(tcb_dest, TCB1))
    shutil.copyfile(os.path.join(tcb_source, TCB2), os.path.join(tcb_dest, TCB2))


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
        

def safe_copy_tcb_files():
    try:
        copy_tcb_files()
    except IOError:
        sleep(6)
        copy_tcb_files()


def stop_dae(error_no):
    """
    Stop the dae.
    
    :return:
    """
    stop_ioc(DAE, error_no)
    sleep(3)
    killproc("ISISDAE-IOC-01.exe")
    sleep(1)
    killproc("isisicp.exe")


def delete_dae_experiments_file(error_no):
    """
    Delete dae experiments file.
    
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
        _log_and_exit("Can not delete data dir! " + str(os_error.strerror), error_no)


def reset_ibex_backend():
    """
    Reset the ibex backend.
    
    :return:
    """

    # stop the block server
    # procServ is set to autorestart the block server, so we need to toggle the autorestart flag first
    safe_execute(toggle_ioc_autorestart, SafeExErrNum.BS_TOGGLE_OFF, BLOCKSERVER, ErrNum.BS_TOGGLE_OFF)
    safe_execute(stop_ioc, SafeExErrNum.BS_STOP, BLOCKSERVER, ErrNum.BS_STOP)
    safe_execute(toggle_ioc_autorestart, SafeExErrNum.DAE_TOGGLE_OFF, DAE, ErrNum.DAE_TOGGLE_OFF)
    safe_execute(stop_dae, SafeExErrNum.DAE_STOP, ErrNum.DAE_STOP)

    # rb numbers
    safe_execute(reload_rb_numbers, SafeExErrNum.RELOAD_RB_NUMBERS, ErrNum.RELOAD_RB_NUMBERS)
    
    # delete test artefacts
    configurations_path = os.path.join(PATH_TO_ICPCONFIGROOT, "configurations")
    print "Removing test configurations in {0}".format(configurations_path)
    safe_execute(remove_test_dir_and_files, SafeExErrNum.REMOVE_TEST_DIR, configurations_path)

    components_path = os.path.join(PATH_TO_ICPCONFIGROOT, "components")
    print "Removing test components in {0}".format(components_path)
    safe_execute(remove_test_dir_and_files, SafeExErrNum.REMOVE_TEST_DIR_2, components_path)

    synoptics_path = os.path.join(PATH_TO_ICPCONFIGROOT, "synoptics")
    print "Removing test synoptics in {0}".format(synoptics_path)
    safe_execute(remove_test_dir_and_files, SafeExErrNum.REMOVE_TEST_DIR_3, synoptics_path)

    safe_execute(safe_set_default_config, SafeExErrNum.SET_DEFAULT_CONFIG, configurations_path)
    safe_execute(safe_copy_dae_tables, SafeExErrNum.COPY_DAE)
    safe_execute(safe_copy_tcb_files, SafeExErrNum.COPY_TCB)
    safe_execute(_delete_data_del_dir, SafeExErrNum.DELETE_DATA_DEL)
    
    safe_execute(delete_dae_experiments_file, SafeExErrNum.DELETE_DATA, ErrNum.DELETE_DATA)
    safe_execute(_delete_data_del_dir, SafeExErrNum.DELETE_DATA_DEL_2)
    print "Deleted the moved data dir"
       

    # reboot the block server by restoring the autorestart flag
    safe_execute(toggle_ioc_autorestart, SafeExErrNum.BS_TOGGLE_ON, BLOCKSERVER, ErrNum.BS_TOGGLE_ON)
    # DAE should be started by block server
    # safe_execute(toggle_ioc_autorestart, SafeExErrNum.DAE_TOGGLE_ON, DAE, ErrNum.DAE_TOGGLE_ON)


def _log_and_exit(error, exit_code):
    """
    Log the error and exit.
    
    :param error: error to log
    :param exit_code: error number to exit with
    :return:
    """
    with file(LOG_FILE, mode="a") as f:
        f.write("Error {0}, {1}: {2}\n".format(exit_code, dt.now().strftime("%d/%m/%y %H:%M:%S"), error))

    print error

    exit(exit_code)


def _delete_data_del_dir():
    """
    Delete the old data to delete dir.
    
    :return:
    """
    path_to_dae_data_del = PATH_TO_DAE_DATA + "del"
    if not os.path.exists(path_to_dae_data_del):
        return
    try:
        os.rename(path_to_dae_data_del+r"\log", r"c:\ISIS_log\log_" + build_number + "_%d" % int(time.time()))
    except:
        pass
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
        shutil.rmtree(path_to_dae_data_del, onerror=error_remove_readonly)
    except OSError:
        sleep(3)
        shutil.rmtree(path_to_dae_data_del, onerror=error_remove_readonly)


def stop_ioc(console_name, error_no):
    """
    Stop an ioc running in a console. ProcServ will automatically restart it if it is set to do so.
    
    :param console_name: name of the console
    :param error_no: number reported in case of error
    :return:
    """
    _send_via_console(console_name, CAN_SIGNAL, error_no)
    print("Stopped or restarted the {0}".format(console_name))


def toggle_ioc_autorestart(console_name, error_no):
    """
    Toggle the procServ autorestart flag in a console.
    
    :param console_name: name of the console
    :param error_no: number reported in case of error
    :return:
    """
    _send_via_console(console_name, DC4_SIGNAL, error_no)
    print("Toggled autorestart for the {0}".format(console_name))


def _send_via_console(console_name, message, error_no):
    """
    Open a console in a subprocess.
    
    :param console_name: name of the console
    :param message: message to send to the console
    :param error_no: number reported in case of error
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
        
        
def _send_multiple_lines_via_console(console_name, lines, error_no):
    """
    Open a console in a subprocess and send lines to it waiting for a reply between each line.
    
    :param console_name: name of the console
    :param lines: iterable fo line to send
    :param error_no: number reported in case of error
    :return: the subprocess
    """
    p = subprocess.Popen([PATH_TO_CONSOLE_EXE, "-M", "localhost", console_name],
                         stdin=PIPE, stdout=PIPE, stderr=PIPE)

    # read 5 lines in but do it on another thread so this doesn't block
    readline = ReadLine(p, 5)
    Thread(target=readline.run).start()

    for line in lines:
        p.stdin.write("{0}\n".format(line))
        p.stdin.flush()
        error_code = p.poll()
        if error_code is not None:
            _log_and_exit("console exited with {0}. Las message {1}!".format(error_code, readline.last_line), error_no)

    output, errors = p.communicate(EXIT_CONSOLE_SIGNAL)

    if errors:
        _log_and_exit(errors, error_no)

        
def reload_rb_numbers(error_no):
    """
    Reload rb numbers from the experimental databse file.
    
    :param error_no: number reported in case of error
    :return:
    """
    
    message = ["F",
               os.path.join(CLEAN_IBEX_DIR, "misc", EXP_DB_RBNUMBER_FILE),
               "U"]
    _send_multiple_lines_via_console(EXPDB_CONSOLE_NAME, message, error_no)
    print("RB numbers updated")


def need_run_clean():
    """
    Should we run a clean, only run a clean every RUN_CLEAN_PER tests.
    
    :return: true if clean; false otherwise
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
