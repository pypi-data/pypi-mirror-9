import abc
import functools
import os
import subprocess

import six


class SubprocessError(Exception):
    def __init__(self, cmd, cwd, error):
        super(SubprocessError, self).__init__(
                'Failed to run: "%s" in %s: %s' % (cmd, cwd, error))

class NoTypeError(Exception):
    pass

class UnknownTypeError(Exception):
    pass

class ConfigError(Exception):
    pass

@functools.total_ordering
class Scanner(object, six.with_metaclass(abc.ABCMeta)):
    def __init__(self, name, priority=0):
        """
        @param name         - name of the Scanner.
        @param priority     - Priority for this scanner.  Scanners with a
                              higher priority will be favored for any given
                              path.  If the priority is less than 0, the
                              scanner will be ignored by any automatic
                              scanner picking
        """
        self._name = name
        self._priority = priority


    def __eq__(self, other):
        return (self._name == other._name
                and self._priority == other._priority)

    def __lt__(self, other):
        return self._priority < other._priority

    @abc.abstractmethod
    def is_suitable(self, path):
        """
        Check if this scanner is suitable to run on the given path.

        @param path - path to check
        @return     - True if this scanner is suitable to scan in
                      the specified path
        """
        pass

    @abc.abstractmethod
    def scan(self, path=None, rescan=False):
        """
        Scan for files at the given path.  This assumes that the
        scanner is suitable for scanning (self.is_suitable()).
        If the Scanner is using a cache, then the cache should be
        invalidated and the file list regenerated when rescan is
        True.

        @param path     - path at which to start scanning, if undefined
                          then the current working directory is used
        @param rescan   - force a full rescan of files instead of using
                          a cached list
        @return         - list of detected files
        """
        pass

    def transform(self, path):
        """
        Final tranform for a path.  This can be used to present matches which
        are more user-friendly during the selection process when can later be
        transformed via this method into the required match.

        @param path - path to be transformed
        @return     - the transformed path
        """
        return path


class SimpleScanner(Scanner):
    def __init__(self, name, cmd, priority=0, detect_cmd=None, root_path=None, cache=None):
        """
        Create a scanner.

        @param name         - name of the Scanner.
        @param cmd          - shell command used to scan for files
        @param priority     - Priority for this scanner.  Scanners with a
                              higher priority will be favored for any given
                              path.  If the priority is less than 0, the
                              scanner will be ignored by any automatic
                              scanner picking
        @param detect_cmd   - If specified, this command will be used to
                              check if this scanner can be used for a
                              given path.  If the command returns 0, the
                              scanner will be used
        @param root_path    - If specified, this path serves two purposes:
                              If no detect_cmd is specified, any path that
                              is a child of the root_path will allow the use
                              of this scanner.  Secondly, when scanning, the
                              current working directory will be set to this
                              path
        @param cache        - If specified, path where this scanner will store
                              a cache of files it scans.  By default, calls
                              to scan will just return the files in the cache.
                              This can be changed by passing rescan=True to
                              scan().
        """
        super(SimpleScanner, self).__init__(name, priority)
        self._cmd = cmd
        self._detect_cmd = detect_cmd
        self._root_path = None
        self._cache = None

        if root_path is not None:
            if root_path.startswith('!'):
                try:
                    c = subprocess.Popen(
                            root_path[1:],
                            shell=True,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
                    stdout, stderr = c.communicate()
                except OSError:
                    raise SubprocessError(root_path[1:], os.path.realpath(os.curdir), stderr)

                if c.returncode != 0:
                    raise SubprocessError(root_path[1:], os.path.realpath(os.curdir), stderr)

                self._root_path = stdout.strip()
            else:
                root_path = os.path.expandvars(root_path)
                root_path = os.path.expanduser(root_path)
                root_path = os.path.normpath(root_path)
                self._root_path = os.path.realpath(root_path)

        if cache is not None:
            cache = os.path.expandvars(cache)
            cache = os.path.expanduser(cache)
            cache = os.path.normpath(cache)
            self._cache = os.path.realpath(cache)

            cachedir = os.path.dirname(os.path.realpath(cache))
            if not os.path.isdir(cachedir):
                os.makedirs(cachedir)

    @classmethod
    def from_configparser(cls, section, parser):
        """
        Create a scanner from a config parser section.

        @param config_section   - config parser object defining a scanner.
        """
        kwds = {}
        if parser.has_option(section, 'detect_cmd'):
            kwds['detect_cmd'] = parser.get(section, 'detect_cmd').replace('\n', ' ')

        if parser.has_option(section, 'root_path'):
            kwds['root_path'] = parser.get(section, 'root_path')

        if parser.has_option(section, 'priority'):
            kwds['priority'] = parser.get(section, 'priority')

        if parser.has_option(section, 'cache'):
            kwds['cache'] = parser.get(section, 'cache')

        cmd = parser.get(section, 'cmd').replace('\n', ' ')

        return cls(section, cmd, **kwds)

    def is_suitable(self, path):
        """
        Check if this scanner is suitable to run on the given path.
        This involves running the detect_cmd to see if we are
        in an appropriate directory type and checking to see if
        the specified path is a descendent of the root_path.

        @param path - path to check
        @return     - True if this scanner is suitable to scan in
                      the specified path
        """
        if self._root_path is not None:
            path = os.path.realpath(os.path.normpath(path))
            if path.startswith(self._root_path):
                return True

        if self._detect_cmd is not None:
            try:
                stderr = ''
                c = subprocess.Popen(
                        self._detect_cmd,
                        cwd=path,
                        shell=True,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
                _, stderr = c.communicate()
            except OSError:
                raise SubprocessError(self._detect_cmd, path, stderr)

            if c.returncode == 0:
                return True

        if self._root_path is None and self._detect_cmd is None:
            return True

        return False

    def scan(self, path=None, rescan=False):
        """
        Scan for files at the given path.  This assumes that the
        scanner is suitable for scanning (self.is_suitable()).
        If a root_path was specified for the command, it is used
        as the current working directory for the command, otherwise
        the path itself is.  If a cache was passed to the
        constructor, the file list will be generated by simply
        reading the cache.  This can be bypassed by setting rescan.


        @param path     - path at which to start scanning, if undefined
                          then the current working directory is used
        @param rescan   - force a full rescan of files instead of using
                          a cached list
        @return         - list of detected files
        """
        have_cache = self._cache is not None and os.path.exists(self._cache)
        ret = None

        if have_cache and not rescan:
            with open(self._cache, 'r') as fp:
                ret = [f.strip() for f in fp.read().split()]
        else:
            if path is None:
                path = os.getcwd()

            cwd = path if self._root_path is None else self._root_path

            try:
                stdout = stderr = ''
                c = subprocess.Popen(
                        self._cmd,
                        cwd=cwd,
                        shell=True,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
                stdout, stderr = c.communicate()
            except OSError:
                raise SubprocessError(self._cmd, cwd, stderr)

            if c.returncode != 0:
                raise SubprocessError(self._cmd, cwd, stderr)

            ret = [f.strip().decode('UTF-8') for f in stdout.split()]

            if self._cache is not None:
                with open(self._cache, 'w') as fp:
                    fp.write(u'\n'.join(ret))

        return ret

    def transform(self, path):
        if self._root_path:
            root_rel_path = os.path.join(self._root_path, path)
            return os.path.normpath(root_rel_path)
        else:
            return path


class StaticScanner(Scanner):
    """
    This class is used to provided a static list of paths. Another way of
    viewing it is that the paths have been pre-scanned and this scanner simply
    serves the result.
    """

    def __init__(self, paths):
        """
        Creates a StaticScanner

        The StaticScanner contains a list of paths that it provides for
        matching. Thus there is no really scanning and all paths are
        automatically suitable.

        @option paths - a list of paths to use for matching

        """
        self._paths = paths

    def is_suitable(self, path):
        """
        Returns True if the path is suitable

        For the StaticScanner, this function always returns True.

        @option path - the path to evaluate
        @return a boolean indicating whether the path is suitable

        """
        return True

    def scan(self, path=None, rescan=False):
        """
        Scan the path for a list of files.

        @param path     - ignore by the StaticScanner
        @param rescan   - ignore by the StaticScanner
        @return         - list of paths contained in the StaticScanner

        """
        return self._paths


def plugin_scanner_from_configparser(section, parser):
    """
    Create a plugin scanner from a config parser section.  A plugin
    scanner is defined in an external python file.  The configparser
    must have the 'path' and 'object' options defined.  Any other
    options (excluding 'type') are passed as keyword arguments to
    the scanner constructor.  Note that each option value passed in
    this manner will be a string.

    @option type    - this must be set to python
    @option path    - path to the python file containing the scanner
    @option object  - name of the scanner object

    @param section  - section of the config defining a Scanner
    @param parser   - parser contining definition
    @return         - Object derived from the base Scanner class as
                      defined by the config section
    """
    if not parser.has_option(section, 'path'):
        raise ConfigError('path not specified for section "%s"' % (section,))

    if not parser.has_option(section, 'object'):
        raise ConfigError('object not specified for section "%s"' % (section,))

    kwds = {}
    for option in parser.options(section):
        if option in ('type', 'path', 'object'):
            continue
        kwds[option] = parser.get(section, option)

    env = {}
    path = parser.get(section, 'path')
    obj = parser.get(section, 'object')

    try:
        with open(path) as fp:
            exec(compile(fp.read(), path, 'exec'), env)
    except Exception as e:
        raise ConfigError('Failed to load plugin "%s": %s' % (
            path, str(e)))

    try:
        scanner = env[obj](**kwds)
    except Exception as e:
        raise ConfigError('Failed to create %s:%s with args %s: %s' % (
            path, obj, str(kwds), str(e)))

    if not isinstance(scanner, Scanner):
        raise ConfigError('%s:%s is not an instance of fzsl.Scanner' % (
            path, obj))

    return scanner

def scanner_from_configparser(section, parser):
    """
    Create a Scanner from a config parser section.

    @param section  - section of the config defining a Scanner
    @param parser   - parser contining definition
    @return         - Object derived from the base Scanner class as
                      defined by the config section
    """
    if not parser.has_option(section, 'type'):
        raise NoTypeError('type not specified for section "%s"' % (section,))

    scanner_type = parser.get(section, 'type')

    if scanner_type == 'simple':
        scanner = SimpleScanner.from_configparser(section, parser)
    elif scanner_type == 'python':
        scanner = plugin_scanner_from_configparser(section, parser)
    else:
        raise UnknownTypeError('Unknown type "%s" for section "%s"' % (
            scanner_type, section))

    return scanner

