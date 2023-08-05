Path Overrides
==============

Detects executables which 'override' other executables in the system PATH.

Install
-------

``path_overrides`` has been tested on recent OS X and Linux systems. It should work on any POSIX system.

To install, simply run::

    $ pip install --user path_overrides

or similar.  Installing the Python package ``blessings`` is recommended to provide colourised output, but is not required.

Use
---

Run ``path_overrides``. It will display a list of which executables shadow other (different) executables.

Motivation
----------

If I press the 'tab' key a couple of times on a recent Linux or OS X shell, I get a prompt looking something like::

    Display all 2228 possibilities? (y or n)

There are over 2000 commands all ready and waiting to be run at a single word being entered. And these don't all live in one place; they live in a (typically small) number of different locations, which are listed in the ``PATH`` environment variable. ``PATH`` is an ordered sequence of paths which are searched to find an executable which will be run. This works well for the most part, but as with all things where there isn't a single namespace, collisions happen. There could be a number of items all with the same name living in different paths all in ``PATH``. In normal use this isn't a problem; ``PATH`` is ordered, and each part of it is a unique no-collisions-possible directory. There is never non-determinism about which executable will 'win', and the ``which`` shell program will report on 'which' path has precedence.

However, unless you are in the habit of regularly running ``which`` before executing any command - or only ever run commands with absolute pathnames - there can be surprises; if someone places a executable earlier in the ``PATH`` than the one you would expect to be run, it will take precendence. ``path_overrides`` will report on any command which overrides a *different* command later in the ``PATH``. Note it's quite common to have symlinks from (e.g.) ``/usr/bin`` to programs in ``/bin``; since they represent 'the same command', ``path_overrides`` will ignore these.

Example
-------

This is a run of ``path_overrides`` on an OS X machine, currently working in a virtualenv. If ``blessings`` is installed, the output will be colourised.

::

    ben$ path_overrides 
    /Users/ben/.virtualenvs/path_overrides/bin/python overrides /usr/bin/python
    /Users/ben/.virtualenvs/path_overrides/bin/easy_install overrides /usr/bin/easy_install
    /Users/ben/.virtualenvs/path_overrides/bin/python2.7 (python) overrides /usr/bin/python2.7 (../../System/Library/Frameworks/Python.framework/Versions/2.7/bin/python2.7)
    /Users/ben/.virtualenvs/path_overrides/bin/easy_install-2.7 overrides /usr/bin/easy_install-2.7
    /Users/ben/.virtualenvs/path_overrides/bin/pip overrides /usr/local/bin/pip
    /Library/Frameworks/Python.framework/Versions/3.4/bin/2to3 (2to3-3.4) overrides /usr/bin/2to3
    /usr/bin/ndisasm overrides /usr/local/bin/ndisasm (../Cellar/nasm/2.11.02/bin/ndisasm)
    /usr/bin/2to3 overrides /usr/local/bin/2to3 (../../../Library/Frameworks/Python.framework/Versions/3.4/bin/2to3)
    /usr/bin/nasm overrides /usr/local/bin/nasm (../Cellar/nasm/2.11.02/bin/nasm)
    /usr/local/bin/libpng-config (../Cellar/libpng/1.6.10/bin/libpng-config) overrides /opt/X11/bin/libpng-config (libpng15-config)
    /usr/local/bin/fc-match (../Cellar/fontconfig/2.11.1/bin/fc-match) overrides /opt/X11/bin/fc-match
    /usr/local/bin/fc-list (../Cellar/fontconfig/2.11.1/bin/fc-list) overrides /opt/X11/bin/fc-list
    /usr/local/bin/fc-cat (../Cellar/fontconfig/2.11.1/bin/fc-cat) overrides /opt/X11/bin/fc-cat
    /usr/local/bin/fc-cache (../Cellar/fontconfig/2.11.1/bin/fc-cache) overrides /opt/X11/bin/fc-cache
    /usr/local/bin/fc-scan (../Cellar/fontconfig/2.11.1/bin/fc-scan) overrides /opt/X11/bin/fc-scan
    /usr/local/bin/freetype-config (../Cellar/freetype/2.5.3_1/bin/freetype-config) overrides /opt/X11/bin/freetype-config
    /usr/local/bin/fc-validate (../Cellar/fontconfig/2.11.1/bin/fc-validate) overrides /opt/X11/bin/fc-validate
    /usr/local/bin/fc-query (../Cellar/fontconfig/2.11.1/bin/fc-query) overrides /opt/X11/bin/fc-query
    /usr/local/bin/fc-pattern (../Cellar/fontconfig/2.11.1/bin/fc-pattern) overrides /opt/X11/bin/fc-pattern

Options
-------

In most cases ``path_overrides`` does not require any options to be provided, but some exist for occasions such as checking the PATH within an alternate root (e.g. when building an alternate chroot filesystem).

In this case, an explicit PATH can be provided as an argument to the `--path` argument. An alternate to the default PATH separator (e.g. ':' on POSIX systems, ';' on Windows) can also be provided via the `--path-sep` argument. Finally, a `--root-dir` path can be specified which all PATH elements will be considered to be local to. Note that the `--root-dir` value will not be included in the output which ``path_overrides`` gives; it is assumed that the calling program / user is aware of this and the more concise information is preferable.

The following example shows the use of all these options::

    $ mkdir -p ~/bin ~/sbin
    $ touch ~/bin/{x,y} ~/sbin/{x,y}
    $ chmod +x ~/bin/{x,y} ~/sbin/{x,y}
    $ path_overrides --path-sep=' ' --path='/bin /sbin' --root-dir='~'
    /bin/y overrides /sbin/y
    /bin/x overrides /sbin/x


Help
----

Help is obtained with the `--help` argument; the version of ``path_overrides`` is reported with `--version`::


    Usage: path_overrides [-h] [--version] [-p PATH] [--path-sep PATH_SEP]
                          [--root-dir ROOT_DIR]

    Display executables in the PATH which override other (different) programs
    later in the PATH

    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit
      -p PATH, --path PATH  provide custom PATH value directly rather than from
                            environment
      --path-sep PATH_SEP   path separator; defaults to system default
      --root-dir ROOT_DIR   assumed root of PATH if given


@codedstructure 2014-2015
