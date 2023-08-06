# Copyright 2011-2015 梅濁酒(umedoblock)

import curses
import re
import locale
import os, sys

import lib
lib.sys_path_append_parent_dir(__file__, 1)

from iasap.lib import logger, start_logger

# locale.setlocale(locale.LC_ALL, "")

__all__ = ["IasapCurses"]

class OneLineState(object):
    def __init__(self, mode):
        self.oneline = ""
        self.cursor_x = 0
        self.buffer = ""
        if not mode in ("vim", "emacs"):
            raise ValueError("unknown mode=\"{}\", mode must be \"vim\" or \"emacs\"")
        self.mode = mode

    def update(self, keyname):
        if self.mode == "vim":
            pass
        elif self.mode == "emacs":
            self._mode_emacs(keyname)

        if self.cursor_x < 0:
            self.oneline = ""
            self.cursor_x = 0

    def check_current(self):
        return self.oneline, self.cursor_x

    def _mode_emacs(self, keyname):
        oneline = self.oneline
        cursor_x = self.cursor_x
        buffer = self.buffer

        logger.debug('oneline="{}", cursor_x={}, buffer="{}" enter in _mode_emacs(keyname="{}")'.format(oneline, cursor_x, buffer, keyname))
        if keyname == "^A":
            # ctr-a     "^A"
            cursor_x = 0
        elif keyname == "^K":
            buffer = oneline[cursor_x:]
            oneline = oneline[:cursor_x]
        elif keyname == "^F":
            cursor_x += 1
            if cursor_x > len(oneline):
                cursor_x = len(oneline)
        elif keyname == "^Y":
            oneline = "".join((oneline[:cursor_x], buffer, oneline[cursor_x:]))
        elif keyname == "^T":
            if len(oneline) >= 2 and cursor_x <= len(oneline) - 2:
                c0 = oneline[cursor_x+0]
                c1 = oneline[cursor_x+1]
                left = oneline[:cursor_x]
                right = oneline[cursor_x+2:]
                oneline = left + c1 + c0 + right
        elif keyname == "^E":
            cursor_x = len(oneline)
        elif keyname == "^D":
            oneline = oneline[:cursor_x] + oneline[cursor_x+1:]
        elif keyname == "^B":
            if cursor_x > 0:
                cursor_x -= 1
        elif keyname == "^W":
            if not cursor_x:
                pass
            elif oneline[cursor_x-1] == " ":
                while cursor_x > 0 and oneline[cursor_x-1] == " ":
                    oneline = oneline[:cursor_x-1] + oneline[cursor_x:]
                    cursor_x -= 1
            else:
                while cursor_x > 0 and oneline[cursor_x-1] != " ":
                    oneline = oneline[:cursor_x-1] + oneline[cursor_x:]
                    cursor_x -= 1
        elif keyname in ("^H", "^?"):
            # ctr-h     "^H"
            # backspace "^?"
            if not cursor_x:
                pass
            else:
                oneline = oneline[:cursor_x-1] + oneline[cursor_x:]
                cursor_x -= 1
        elif len(keyname) >= 2:
            pass
        elif re.search("[-a-zA-Z0-9 &|]", keyname):
            # ord("a") => 0x61
            # chr(0x61) => "a"
            oneline = oneline[:cursor_x] + keyname + oneline[cursor_x:]
            cursor_x += 1

        self.oneline = oneline
        self.cursor_x = cursor_x
        self.buffer = buffer

        logger.debug('oneline="{}", cursor_x={}, buffer="{}" leave out _mode_emacs(keyname="{}")'.format(oneline, cursor_x, buffer, keyname))

class IasapCurses(object):
    MAX_LENGTH = 80
    MAX_HEIGHT = 30

    def __init__(self, height=MAX_HEIGHT):
        self.stdscr = curses.initscr()
        curses.noecho()
        self.stdscr.nodelay(False)
        self._height = height
        self._ols = OneLineState("emacs")

    def getch(self, y, x):
        ch = self.stdscr.getch(y, x)
        if ch == 3:
            # enable Ctr-c in windows.
            logger.debug("stdscr.getch() raise KeyboardInterrupt.")
            raise KeyboardInterrupt
        return ch

    def _init_screen(self):
        self.stdscr.erase()

    def _draw_oneline(self, oneline):
        self.stdscr.addstr(0, 0, oneline)

    def _get_new_ch(self, cursor_x):
        try:
            new_ch = self.getch(0, cursor_x)
        except KeyboardInterrupt:
            new_ch = "__break__"

        logger.debug("new_ch = {} in _get_new_ch()".format(new_ch))
        return new_ch

    def _update_oneline(self, oneline, cursor_x, keyname):
        old_oneline, old_cursor_x = self._ols.check_current()
        self._ols.update(keyname)

        new_query = False
        if self._ols.oneline != old_oneline:
            new_query = True

        return self._ols.oneline, self._ols.cursor_x, new_query

    def get_body(self, query):
        body = "\n".join([query] * self._height)
        return body

    def _draw_line(self, line, ss, y, width, effect):
      self.stdscr.addstr(y, 0, line, effect)
      # try:
      #     self.stdscr.addstr(y, 0, line, effect)
      #     return True
      # except curses.error as raiz:
      #     self.stdscr.addch(0, len(ss) - 1, " ")
      #     # ss = ss[:-1]
      #     self.stdscr.addstr(0, 0, ss)
      #     args = raiz.args
      #     message = "raised error reason: {}".format(args[0])
      #     return False
      #     # self.stdscr.addstr(1, 0, message)

    def _effect_line(self, line, ss, y, width, effect):
        # count ascii charactor to ascii_counter
        for ascii_counter, c in enumerate(line):
            if len(c.encode()) > 1:
                break
        ss_lower = ss.lower()
        len_ss = len(ss)

        x = 0
        while True:
            try:
                rel_index = line.lower().index(ss_lower)
            except ValueError as raiz:
                args = raiz.args
                if args[0] == "substring not found":
                    break
                else:
                    logger.debug("args = {}, in _effect_line()".format(args))
                    raise ValueError(*args)
            else:
                x += rel_index
                if x < width and x < ascii_counter:
                    rev = line[rel_index:rel_index+len_ss]
                    self.stdscr.addstr(y, x, rev, effect)
                    x += len_ss
                    line = line[rel_index+len_ss:]
                else:
                    break

    def start(self):
        # for organize with OneLineTkinter class.
        self.run()

    def run(self):
        new_ch_no = 0
        cursor_x = 0
        oneline = ""
        while True:
            logger.debug("new_ch_no = {} ==================".format(new_ch_no))
            ymax, xmax = self.stdscr.getmaxyx()
            new_ch = self._get_new_ch(cursor_x)
            new_ch_no += 1
            if new_ch == "__break__":
                self.stdscr.erase()
                break
            keyname = curses.keyname(new_ch)
            logger.debug("keyname = \"{}\", len(keyname) = {}, type(keyname) = {}, in run()".format(keyname, len(keyname), type(keyname)))
            keyname = keyname.decode()
            logger.debug("keyname = \"{}\", len(keyname) = {}, type(keyname) = {}, in run()".format(keyname, len(keyname), type(keyname)))
            oneline, cursor_x, new_query = \
                self._update_oneline(oneline, cursor_x, keyname)

            if not len(oneline) < xmax:
                oneline = oneline[:xmax - 1]
                cursor_x -= 1

            if not oneline and not cursor_x:
                self.stdscr.erase()
            if re.search("^ *$", oneline) or not new_query:
                continue

            self._init_screen()
            self._draw_oneline(oneline)

            height = ymax - 1
            width = xmax
            curses_lines = self.get_body(oneline)
            lines = curses_lines.split("\n")
            offset_y = 1
            for i, line in enumerate(lines):
              # logger.debug("i={}, line={}".format(i, line)) OK
                try:
                    self._draw_line(line, oneline, i + offset_y, \
                                       width, curses.A_NORMAL)
                except curses.error as raiz:
                    break

        self.stdscr.erase()
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()
        logger.debug("oneline_curses finished.")

if __name__ == "__main__":
    start_logger(__file__, os.path.curdir, logger.DEBUG)

    iac = IasapCurses(20)
    iac.run()
