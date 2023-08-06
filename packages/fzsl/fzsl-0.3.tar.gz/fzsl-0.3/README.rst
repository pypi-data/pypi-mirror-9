===========
FuZzy SheLl
===========

.. image:: https://travis-ci.org/jsbronder/fzsl.svg?branch=master
    :target: https://travis-ci.org/jsbronder/fzsl

Introduction
------------

Fuzzy file or path searcher in the shell which provides path completion similar
to the ctrlp_ plugin for vim.  Start a command and then hit Ctrl+p to see a list
of possible paths.  Enter search terms to narrow down the list and then select
the appropriate completion using your arrow keys or Ctrl+j/k.

fzsl uses a single matching algorithm but provides the user with a wide variety
of ways to influence how file scanning is performed as it is by far the most
intensive part of this process.  Scanners are selected by first checking if
they are valid for the current working directory and then ranked by a
user-selected priority.

Configuration
-------------
All configuration of fzsl is done in an ini style which is interpreted by the
python ConfigParser module.  Each section defines a new scanner with the
section title used as the scanner name.  Configuration is read from
*~/.config/fzslrc* if it exists, if not fzsl will fall back to
*/usr/share/fzsl/fzsl.conf*.  The default configuration that ships with fzsl contains
full documentation for all scanner types and should be referenced.  It
currently handles standard directories, git checkouts and scanning for only
directories.  It also has a number of examples for how to define additional
scanners.  Scanners with a priority less than 0 can only be used by passing the
scanner name to fzsl with the **--rule** argument.

Simple Scanners
---------------
Simple scanners use shell commands and or functions to check if they are suitable
and to scan for files.  They are very easy to configure and should support the
vast majority of use cases.  Simple scanners are defined by setting two shell
commands that should be executed.  The first detects if the scanner is suitable
for the current working directory and the second performs the scanning.  Simple
scanners should also set a priority for ranking if more than one scanner is
valid.  If the priority is not specified, it defaults to 0.  Finally, a cache
and root path for the scanning command can be set.  For example::

    # Standard git rule
    [git]
    type = simple
    detect_cmd = git rev-parse
    cmd = git ls-files
    priority = 10

    # If the directory has a large number of files such that scanning
    # takes too long, a cache can be used.  The cache can be regenerated
    # by an external script or by pressing F5 or ctrl+r in the UI.
    [linux]
    type = simple
    root_path = /usr/src/linux
    cmd = find .
    cache = ~/.fzsl-cache/linux

The only requirement for the **cmd** and **detect_cmd** is that they are
available in your standard login shell.  For instance, if using bash, they
should be defined in *~/.bash_profile*::

    [shell-function-scanner]
    type = simple
    detect_cmd = my_detect_function
    cmd = my_scanning_function
    priority = 100

**Options**:

**type**
    This must be set to **simple**.

**cmd**
    The command to execute in the root directory that will output all possible
    matches.  By default, the current working directory of the command will be
    the same as that of the caller.  However, if the root_path is specified, it
    will be used instead.

**detect_cmd**
    This command will be executed to determine if the scanner is a possible
    match for the current working directory.  The command should return 0 for a
    valid directory.

**root_path**
    The root path has two possible uses.  First, if the current working
    directory is a subdirectory of the root path, the scanner will be
    considered suitable for use when scanning.  Second, if the root_path is
    specified along with detect_cmd, then the root_path will be used as the
    current working directory when executing the detect_cmd.

    To use the stdout of a command rather than a fixed string as the root_path,
    preface the root_command with a **!**.  For example,::

        root_path = !echo "my/root/path"

**priority**
    The priority is used to determine which scanner to use when multiple
    scanners are considered suitable.  The higher the priority, the more likely
    it will be selected.  Scanners with a priority less than 0 are never
    considered unless manually selected via the **--rule** argument.

**cache**
    Path to a file that will be used to cache results for for this scanner.  By
    default, scanners will use the cache rather than rescanning the entire file
    list.  Note that the cache is tied to the scanner, so if the same **cmd**
    needs to be used with two different caches, it will have to be two
    different scanners.  If no cache is supplied, results will just be
    regenerated on each run.  This is probably fine unless you have a really
    large number of files (tens of thousands) to scan or a really slow disk.

Python Scanners
---------------
Python scanners offer a deeper level of customization for scanners.  They must
derive from the **fzsl.Scanner** class.  See ``pydoc fzsl.Scanner``.  The
priority attribute should be set and the methods ``is_suitable(self, path)``
and ``scan(self, path=None, rescan=False)`` need to be defined.  Any caching is
left up to the implementor.  Any extra options set in the scanner configuration
are passed to the scanners ``__init__`` method as keyword arguments.  Perhaps
the best example is to show how one could create a Simple Scanner using fzsl
itself::

    # Example plugin file that loads the default simple scanner.
    [default-via-plugin]
    type = python
    path = /usr/lib/python2.7/site-packages/fzsl/scanner.py
    object = SimpleScanner
    # The following are passed as keyword arguments to the
    # RuleScanner constructor
    cmd = find .
    priority = 0

**Options**:

**type**
    This must be set to **python**.

**path**
    Path to the python file containing the scanner implementation.

**object**
    Name of the ``fzsl.Scanner`` derived class.

**\***
    Any further options are passed as keyword arguments to the Scanners
    constructor.  Note that as they are parsed by **ConfigParser** they
    will be strings.

Installation
------------
fzsl can be installed via pip or by simply running the included ``setup.py``
script::

    pip install fzsl
    # OR
    python setup.py install --root <destination> --record installed_files.txt

Shell Functions
---------------
fzsl will not modify your shell by default.  It is up to you to source the
included */usr/share/fzsl/fzsl.bash*.  It defines two functions that will add
fzsl functionality directly to your shell.  See the script for further
documentation.

- ``__fzsl_bind_default_matching [BINDING]``:  Binds ctrl-p to launch fuzzy
  scanning.  If ctrl-p is not desired, another readline style keybinding can be
  specified.  When launched, fzsl will scan the current directory and provide a
  UI for updating the current query for fuzzy matching.  On completion the
  current command line will be preserved and the matched path will be appended.

- ``__fzsl_create_fzcd [SCANNER]"``:  Creates the ``fzcd`` function which will
  change the current directory to the fuzzily matched path on completion. By
  default the shipped **dirs-only** scanner will be used.  Another scanner can
  be specified by passing it as the first argument.

Fuzzy Matching User Interface
-----------------------------
fzsl will launch a ncurses interface when prompted to start matching in the
current directory.  Once the file list has been populated by the scanner, the
user can begin to input characters to be fuzzily matched against the scanned
paths.  As the query is updated, the list of available paths will be trimmed.
A portion of each path will be highlighted to represent which part of it was
best matched against the query.  The user can also move the cursor around to
support editing of the query.  The following keybindings are defined.

- **Enter**:  Finish completion and echo the currently selected path, if any.
- **Down Arrow**/**ctrl+j**:  Select the next path in the list.
- **Up Arrow**/**ctrl+k**:  Select the previous path in the list.
- **Left Arrow**:  Move the cursor left.
- **Right Arrow**:  Move the cursor right.
- **ctrl+v**:  Enter verbose move which shows the scores for each path.
- **Escape**/**ctrl+c**:  Exit the UI without echoing the currently selected path.
- **Backspace**:  Delete the character behind the cursor.
- **F5**/**ctrl+r**: If the scanner has a cache, refresh it.

Errata
------
:Author:
    Justin Bronder <jsbronder@gmail.com>

:Contributers:
    Joshua Downer <joshua.downer@gmail.com>

:License:
    BSD

:Source/Homepage:
    http://github.com/jsbronder/fzsl

.. _ctrlp: https://github.com/kien/ctrlp.vim
