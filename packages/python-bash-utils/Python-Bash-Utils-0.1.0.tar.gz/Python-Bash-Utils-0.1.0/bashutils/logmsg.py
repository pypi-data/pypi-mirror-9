#!/usr/local/bin/python
# coding: utf-8

# -----------------------------------------------------------------------------

import sys

# 3rd Party
from colors import *

# -----------------------------------------------------------------------------
# User feedback
# -----------------------------------------------------------------------------
# Divider line
def log_divline():
    print "-"*80

# Header logging
def log_header(string):
    print color_text('==> ', 'green') + color_text(string, 'white')

# Success logging
def log_success(string):
    print color_text('[✓] ', 'green') + string

# Error logging
def log_error(string):
    print color_text('[✗] ', 'magenta') + string

# Warning logging
def log_warning(string):
    print color_text('[!] ', 'yellow') + string

# Info logging
def log_info(string):
    print color_text('[i] ') + string

# User declined logging
def log_declined(string):
    print color_text('[✗] ', 'magenta') + color_text(string, 'cyan') + \
        color_text(' declined. ') + color_text('Skipping...', 'green')

# -----------------------------------------------------------------------------
# User Input
# -----------------------------------------------------------------------------
# Prompt user for input
def prompt(question):
    response = raw_input( color_text('[?] ', 'yellow') + color_text(question, 'cyan') + ' ' )
    return response

# Ask user to confirm
def confirm(question):
    response = raw_input( color_text('[?] ', 'yellow') + color_text(question, 'cyan') + '? (y/n) ' )
    if response in ['y', 'yes']:
        return True
    else:
        log_declined(question)
        return False

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    log_divline()
    log_header('header')
    log_success('success')
    log_error('error')
    log_warning('warning')
    log_info('info')
    log_declined('something')

    answer = prompt('What is your name?')
    print answer

    if confirm('Confirm this'):
        print 'You confirmed!'
