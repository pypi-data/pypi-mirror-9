#!/usr/local/bin/python
# coding: utf-8

# -----------------------------------------------------------------------------

# Python
import os
import platform
import shutil
import subprocess

# 3rd party
from colors import *
from logmsg import *

# -----------------------------------------------------------------------------
# Get OS
# -----------------------------------------------------------------------------
def get_os():
    uname = platform.system()
    if uname == 'Darwin':
        return 'OSX'

    if uname == 'Linux':
        find = ['Fedora', 'CentOS', 'Debian', 'Ubuntu']
        # If lsb_release then test that output
        status, stdout, stderr = exec_cmd('hash lsb_release &> /dev/null')
        if status:
            for search in find:
                status, stdout, stderr = exec_cmd('lsb_release -i | grep %s > /dev/null 2>&1' % search)
                if status:
                    return search

        # Try to cat the /etc/*release file
        else:
            for search in find:
                status, stdout, stderr = exec_cmd('cat /etc/*release | grep %s > /dev/null 2>&1' % search)
                if status:
                    return search

    return 'unknown'

# -----------------------------------------------------------------------------
# Execute Command
# -----------------------------------------------------------------------------
def exec_cmd(cmd):
    # call command
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)

    # talk with command i.e. read data from stdout and stderr. Store this info in tuple
    stdout, stderr = p.communicate()

    # wait for terminate. Get return returncode
    status = p.wait()
    if status == 0:
        status = True
    else:
        status = False

    return (status, stdout, stderr)

# Check if command exists
def cmd_exists(program):
    cmd = "where" if platform.system() == "Windows" else "which"
    status, stdout, stderr = exec_cmd('{0} {1}'.format(cmd, program))
    return status

# -----------------------------------------------------------------------------
# Files / Directory
# -----------------------------------------------------------------------------
# Check if file exists
def file_exists(filepath):
    if os.path.isfile(filepath):
        return True

    return False

# Delete file
def delete_file(filepath):
    if os.path.isfile(filepath):
        os.remove(filepath)
        return True

    return False

# Check if dir exists
def dir_exists(directory):
    d = os.path.dirname(directory)
    if os.path.exists(d):
        return True

    return False

# Create dir
def make_dir(directory):
    d = os.path.dirname(directory)
    if not os.path.exists(d):
        os.makedirs(d)

# Delete dir
def delete_dir(directory):
    d = os.path.dirname(directory)
    if os.path.exists(d):
        shutil.rmtree(directory)

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    pass
