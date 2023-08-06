#!/usr/local/bin/python
# coding: utf-8

import json
import os
import subprocess
import shutil
import platform

# -----------------------------------------------------------------------------
# Shared Variables
# -----------------------------------------------------------------------------
class color:
    RED     = '\033[91m'
    GREEN   = '\033[92m'
    YELLOW  = '\033[93m'
    BLUE    = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN    = '\033[96m'
    WHITE   = '\033[97m'
    GREY    = '\033[37m'
    RESET   = '\033[0m'

# -----------------------------------------------------------------------------
# User Feedback
# -----------------------------------------------------------------------------
# Divider line
def divline():
    print "-"*80

# Script header
def script_header(string):
    divline()
    print "{0}{1}{2} | Author: Tim Santor {3}<tsantor@xstudios.agency>{4}".format(color.WHITE, string, color.RESET, color.GREY, color.RESET)
    divline()

# Header logging
def e_header(string):
    print "{0}==> {1}{2}{3}".format(color.GREEN, color.WHITE, string, color.RESET)

# Success logging
def e_success(string):
    print "{0}[✓] {1}{2}".format(color.GREEN, string, color.RESET)

# Error logging
def e_error(string):
    print "{0}[✗] {1}{2}".format(color.MAGENTA, string, color.RESET)

# Warning logging
def e_warning(string):
    print "{0}[!] {1}{2}".format(color.YELLOW, string, color.RESET)

# Info logging
def e_info(string):
    print "{0}[→] {1}{2}".format(color.GREY, string, color.RESET)

# User declined logging
def e_declined(string):
    print "{0}[✗] {1}{2}{3} declined. {4}Skipping...{5}".format(color.YELLOW, color.CYAN, string, color.RESET, color.GREEN, color.RESET)

# -----------------------------------------------------------------------------
# User Input
# -----------------------------------------------------------------------------
def confirm(question):
    response = raw_input("{0}[?] {1}{2}?{3} (y/n) ".format(color.YELLOW, color.CYAN, question, color.RESET))
    if response == 'y':
        return True
    else:
        e_declined(question)
        return False

# -----------------------------------------------------------------------------
# Execute Command
# -----------------------------------------------------------------------------
def exec_cmd(cmd):
    # call date command ##
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)

    # talk with command i.e. read data from stdout and stderr. Store this info in tuple
    output, err = p.communicate()

    # wait for terminate. Get return returncode
    p_status = p.wait()
    if p_status == 0:
        p_status = True
    else:
        p_status = False

    return {
        'output': output,
        'status': p_status
    }

# Check if command exists
def cmd_exists(program):
    cmd = "where" if platform.system() == "Windows" else "which"
    rc = exec_cmd('{0} {1}'.format(cmd, program))
    return rc['status']

# -----------------------------------------------------------------------------
# Files / Directory
# -----------------------------------------------------------------------------
# Check if file exists
def file_exists(filename):
    if os.path.isfile(filename):
        return True

    return False

# Check if dir exists
def dir_exists(directory):
    d = os.path.dirname(directory)
    if os.path.exists(d):
        return True

    return False

# Ensure dir exists
def ensure_dir(directory):
    d = os.path.dirname(directory)
    if not os.path.exists(d):
        os.makedirs(d)

# Delete dir
def delete_dir(directory):
    d = os.path.dirname(directory)
    if os.path.exists(d):
        shutil.rmtree(directory)

# -----------------------------------------------------------------------------
