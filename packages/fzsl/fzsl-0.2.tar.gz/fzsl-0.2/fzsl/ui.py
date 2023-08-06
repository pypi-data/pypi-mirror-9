import contextlib
import curses
import os
import sys

import six

import fzsl

for i, color in enumerate(('white', 'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan')):
    vars()['COL_%s' % (color.upper())] = i
    vars()['COL_B%s' % (color.upper())] = i + 8


@contextlib.contextmanager
def ncurses():
    """
    Context manager for curses applications.  This does a number of
    things beyond what curses.wrapper() does.

    - Redirect stdout to stderr.  This is done so that we can still
      use the ncurses interface from within a pipe or subshell.
    - Drop the escape delay down to 25ms, similar to vim.
    - Remove newline mode.

    An ncurses screen is returned by the manager.  If any exceptions
    occur, all of the setup performed by the manager is undone before
    raising the original exception.  This should guarantee that any
    bugs in the code will not leave the user with a messed up shell.
    """
    # Push stdout to stderr so that we still get the curses
    # output while inside of a pipe or subshell
    old_stdout = sys.__stdout__
    old_stdout_fd = os.dup(sys.stdout.fileno())
    os.dup2(sys.stderr.fileno(), sys.stdout.fileno())

    # Reduce the timeout after receiving an escape character, there
    # doesn't seem to be a way to do this via curses so we have to
    # set the environment variable before creating the screen.
    if not 'ESCDELAY' in os.environ:
        os.environ['ESCDELAY'] =  '25'

    scr = curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    _ = [curses.init_pair(i + 1, i, -1) for i in range(curses.COLORS)]

    curses.noecho()
    curses.cbreak()
    curses.raw()
    curses.nonl()
    curses.curs_set(2)
    scr.keypad(1)

    exc = None
    try:
        yield scr
    #pylint: disable=W0703
    except Exception:
        exc = sys.exc_info()

    scr.keypad(0)
    curses.nl()
    curses.nocbreak()
    curses.echo()
    curses.endwin()

    os.dup2(old_stdout_fd, sys.stdout.fileno())
    sys.stdout = old_stdout

    if exc is not None:
        six.reraise(exc[0], exc[1], exc[2])


class SimplePager(object):
    def __init__(self, scr, scanner):
        """
        Create a simple pager for showing scan results.  As new terms
        are entered, the results will be updated with the best matches
        showing a highlight over the part of the string which matched.

        @param scr      - ncurses screen to use
        @param scanner  - fzsl.Scanner object that will be used to
                          generate the list of possible matches
        """
        self._scr = scr
        self._scanner = scanner

        self._show_score = False
        self._fm = fzsl.FuzzyMatch()
        self._selection = 0
        self._search = ''

        y, x = self._scr.getmaxyx()

        self._prompt = curses.newwin(1, x, y-1, 0)
        self._select = curses.newwin(y - 2, x, 0, 0)
        self._max_y = y - 2
        self._max_x = x - 1
        self._cursor_x = 0

    def _draw_select(self):
        """
        Redraw the selection window which contains all of the
        possible matches to the current search.
        """
        self._select.erase()
        m = self._fm.top_matches(self._max_y)
        if self._selection >= len(m):
            self._selection = max(len(m) - 1, 0)

        for index, match in enumerate(m):
            if len(self._search) > 0 and self._fm.score(match) == 0:
                continue

            prefix = u''
            if self._show_score:
                prefix = u'%f     ' % (self._fm.score(match),)
            offset = len(prefix)

            start = self._fm.start(match)
            end = self._fm.end(match)
            if end > 0 and len(self._search) > 0:
                end += 1
            line = self._max_y - index - 1
            decor = 0
            if self._selection == index:
                decor = curses.A_UNDERLINE

            match = match[:self._max_x]
            start = min(start, self._max_x)
            end = min(end, self._max_x)

            self._select.addstr(line, 0, prefix + match[:start], decor)
            if start + offset < self._max_x:
                self._select.addstr(line, start+offset, match[start:end], decor|curses.color_pair(COL_BCYAN))
            if end + offset < self._max_x:
                self._select.addstr(line, end+offset, match[end:], decor)
        self._select.refresh()

    def _draw_prompt(self):
        """
        Redraw the prompt window.
        """
        self._prompt.erase()
        prompt = "%d/%d >" % (self._fm.n_matches, self._fm.n_files)
        search_start = 4 + len(prompt)

        self._prompt.addstr(0, 2, prompt)
        self._prompt.addstr(0, search_start, self._search)
        y, x = self._prompt.getyx()
        self._prompt.move(y, search_start + self._cursor_x)
        self._prompt.refresh()

    def run(self):
        """
        Start the pager.
        """
        self._scr.addstr("Scanning ...")
        self._scr.refresh()
        files = self._scanner.scan()
        self._fm.add_files(files)

        self._draw_select()
        self._draw_prompt()

        while True:
            c = self._scr.getch()
            key = curses.keyname(c).decode('UTF-8')

            if key in (u'^M',):
                # enter
                break
            elif key  in ('KEY_DOWN', '^J'):
                # down arrow, ctrl+j
                self._selection = self._selection - 1 if self._selection > 0 else 0
                self._draw_select()
            elif key  in ('KEY_UP', '^K'):
                # up arrow, ctrl+k
                self._selection = self._selection + 1 if self._selection < self._max_y - 2 else self._selection
                self._draw_select()
            elif key in ('KEY_LEFT',):
                if self._cursor_x > 0:
                    self._cursor_x -= 1
                    self._draw_prompt()
            elif key in ('KEY_RIGHT',):
                if self._cursor_x < len(self._search):
                    self._cursor_x += 1
                    self._draw_prompt()
            elif key in ('^V',):
                # ctrl+v
                self._show_score = not self._show_score
                self._draw_select()
            elif key in ('^[',):
                # escape
                return ''
            elif c in (curses.KEY_RESIZE,):
                y, x = self._scr.getmaxyx()

                # Have to handle the parent screen fully first otherwise updates
                # to the subwindows don't seem to take.
                curses.resizeterm(y, x)
                self._scr.resize(y, x)
                self._scr.erase()
                self._scr.refresh()

                self._max_y = y - 2
                self._max_x = x - 1
                self._cursor_x = x if x < self._cursor_x else self._cursor_x

                self._select.resize(y - 2, x)
                self._draw_select()

                self._prompt.resize(1, x)
                self._prompt.mvwin(y-1, 0)
                self._draw_prompt()
            else:
                if key in ('KEY_BACKSPACE',):
                    # delete, backspace
                    if self._cursor_x > 0:
                        start = self._search[:self._cursor_x - 1]
                        end = self._search[self._cursor_x:]
                        self._search = start + end
                        self._cursor_x -= 1
                elif key in ('^R', 'KEY_F(5)'):
                    self._scr.erase()
                    self._scr.addstr('Scanning ...')
                    self._scr.refresh()
                    files = self._scanner.scan(rescan=True)
                    self._fm.reset_files(files)
                else:
                    start = self._search[:self._cursor_x]
                    end = self._search[self._cursor_x:]
                    self._search = start + chr(c) + end
                    self._cursor_x += 1

                self._fm.update_scores(self._search)

                self._draw_select()
                self._draw_prompt()

        try:
            match = self._fm.top_matches(self._max_y)[self._selection]
            return self._scanner.transform(match)
        except IndexError:
            return ''

