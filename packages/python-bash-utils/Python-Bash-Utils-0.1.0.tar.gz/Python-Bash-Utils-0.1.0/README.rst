Python Bash Utils
=================

Author: Tim Santor tsantor@xstudios.agency
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Overview
--------

Bash color management and log system for Python users.

Requirements
------------

-  Python 2.7.x

    NOTE: This has only been tested on a Mac (10.10.2) at this time.

Installation
------------

You can install directly via pip:

::

    pip install python-bash-utils

Or from the BitBucket repository (master branch by default):

::

    git clone https://bitbucket.org/tsantor/python-bash-utils
    cd python-bash-utils
    sudo python setup.py install

Usage
-----

colors
~~~~~~

Import:

::

    from bashutils import colors

Functions:

::

    colors.color_text(text, color="none")

logmsg
~~~~~~

Import:

::

    from bashutils import logmsg

Functions:

::

    logmsg.log_divline()             # ----------
    logmsg.log_header('header')      # ==> header
    logmsg.log_success('success')    # [✓] success
    logmsg.log_error('error')        # [✗] error
    logmsg.log_warning('warning')    # [!] warning
    logmsg.log_info('info')          # [i] info
    logmsg.log_declined('something') # [✗] something declined. Skipping...

bashutils
~~~~~~~~~

Import:

::

    from bashutils import bashutils

Functions:

::

    bashutils.get_os() # OSX, 'Fedora', 'CentOS', 'Debian', 'Ubuntu'

    status, stdout, stderr = bashutils.exec_cmd('git -h')

    bashutils.cmd_exists('git') # True or False

    bashutils.file_exists('/path/to/file.ext') # True or False
    bashutils.delete_file('/path/to/file.ext') # True or False
    bashutils.dir_exists('/path/to/dir') # True or False
    bashutils.make_dir('/path/to/dir')
    bashutils.delete_dir('/path/to/dir')

Version History
---------------

-  **0.1.0** - Initial release

Issues
------

If you experience any issues, please create an
`issue <https://bitbucket.org/tsantor/banner-ad-toolkit/issues>`__ on
Bitbucket.
