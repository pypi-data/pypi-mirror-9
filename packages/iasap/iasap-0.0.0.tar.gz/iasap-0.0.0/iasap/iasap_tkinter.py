# Copyright 2011-2015 梅濁酒(umedoblock)

import argparse
import re
import tkinter
import tkinter.scrolledtext
import sys, os

_here = os.path.abspath(__file__)
_parent_dir = os.path.join(os.path.dirname(_here), "..")
# print("_parent_dir =", _parent_dir)
sys.path.append(_parent_dir)

from iasap.lib import logger, start_logger

class IasapTkinter(object):
    MAX_LENGTH = 80
    MAX_HEIGHT = 30

    def __init__(self):
        self.root = tkinter.Tk()
        self.used_query = ""
        self.root.option_add("*font", ("Ricty", 14))
        self.root.title("IasapTkinter")
        self.ctrl_key = False
        self.need_to_search = False

        line = " " * self.MAX_LENGTH
        self.buffer_oneline = tkinter.StringVar()
        self.buffer_oneline.set(line)

        # labelの設定
        oneline = tkinter.Text(self.root,
                            height=1,
                            )
        self.oneline = oneline
        oneline.pack(anchor=tkinter.NW,
                  padx=4,
                  )
      # oneline.bind("<Control-KeyPress>", self.ctrl_key_press)
      # oneline.bind("<Control-KeyRelease>", self.ctrl_key_release)
        oneline.bind("<Any-KeyRelease>", self.release_key)
      # oneline.bind("<1>", self.focus_oneline)
        oneline.focus_set()

        # help(tkinter.Widget)
        # help(tkinter.Text)
        # help(tkinter.scrolledtext.ScrolledText)
        body = tkinter.Text( self.root,
                            borderwidth=1,
                          # state=tkinter.NORMAL,
                          # state=tkinter.DISABLED,
                            bg="gray",
                            fg="black",
                            selectbackground="white",
                            wrap=tkinter.WORD,
                            height=self.MAX_HEIGHT,
                            width=self.MAX_LENGTH,
                            relief=tkinter.RIDGE,
                            font=("Helvetica", 12),
                            )
        body.pack(
                 fill=tkinter.BOTH,
                 expand=1,
               # padx=5, pady=5,
               # ipadx=3, ipady=3,
               # side=tkinter.TOP,
                 )
        self.body = body

    def focus_oneline(self, event):
        self.oneline.focus_set()

    def get_key(self, key):
        key = key.encode()
        if key == b"^C":
            self.root.quit()
        if key == b"^H":
            len_ss = len(self.ss)
            self.ss = self.ss[:len_ss-1]
        else:
            self.ss += key
        cursor_x = len(self.ss)
        if cursor_x > self.MAX_LENGTH - 1:
            cursor_x = self.MAX_LENGTH - 1
            self.ss = self.ss[:cursor_x]
        oneline = self.ss
        padding = b" " * (self.MAX_LENGTH - cursor_x)
        oneline = self.ss + padding
        body = key
        self._set_msg(oneline, body, cursor_x)

    def _set_msg(self, oneline, body, cursor_x):
        logger.debug(".index(INSERT) =", self.txt.index(tkinter.INSERT))
        logger.debug(".index(END) =", self.txt.index(tkinter.END))
        sp = self.txt.index(tkinter.INSERT).split(".")
        index_oneline = "{}.0".format(4)
        self.txt.insert(index_oneline, body + b"\n")

    def to_int(self, ss, sep="."):
        return [int(s) for s in ss.split(sep)]

    def get_oneline(self, event):
        logger.debug("in get_oneline()")
        logger.debug("event.(type={}, keycode={}, keysysm={}, keysym_num={}, "
                     "char=\'{}\')".format(event.type, event.keycode,
                                           event.keysym, event.keysym_num,
                                           event.char))
        # index() が値を返す時、"y.x" の形式で、oneline の左端に cursor
        # がある時、返ってくる文字列は、"1.0"。
        # なので、y=1, x=0 が開始っぽい。変なの。こういう癖、好きじゃない。
        cursor_yx = self.oneline.index(tkinter.INSERT)
        logger.debug("cursor_yx={}".format(cursor_yx))
        line, column = self.to_int(cursor_yx)

        current_oneline = self.oneline.get("1.0", tkinter.END)
        current_oneline = re.sub("\n$", "", current_oneline)

        query = current_oneline
        if line > 1:
            # 現在の oneline が複数行だったら。
            # 現在の oneline から改行を削除して、
            # 改行がない値を oneline に設定し直す。
            query = current_oneline.replace("\n", "")

            self.oneline.delete("1.0", tkinter.END)
            self.oneline.insert(tkinter.END, query)
        if self.used_query != query:
            logger.debug('used_query={}, query={}'.format(self.used_query, query))
            self.used_query = query
            self.need_to_search = True
        else:
            self.need_to_search = False
        logger.debug("need_to_search={}.".format(self.need_to_search))

    def update_body(self, body):
        self.body.delete("1.0", tkinter.END)
        self.body.insert(tkinter.END, body)

    def get_body(self, query):
        body = "\n".join([query]  * self.MAX_HEIGHT)
        return body

    def release_key(self, event):
        self.get_oneline(event)
        if self.need_to_search:
            body = self.get_body(self.used_query)
            self.update_body(body)

    def char_key(self, event):
        logger.debug("char_key() keysym =", event.keysym)
        logger.debug("char_key()   char =", event.char)
        d = {
            "BackSpace": "^H",
            "Delete": "^D",
            "Right": "^F",
            "Left": "^B",
        }
        keysym = event.keysym
        if keysym in d:
            char = d[keysym]
        else:
            char = event.char
        if not re.search("[-a-zA-Z0-9 &|]", char):
            return
        self.get_key(char)

    def ctrl_key_press(self, event):
        self.ctrl_key = True

    def ctrl_key_release(self, event):
        self.ctrl_key = False

    def ctrl_key(self, event):
        if not event.char:
            return
        key = "^" + event.keysym.upper()
        self.get_key(key)

    def start(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="tkinter")
    parser.add_argument("--debug", dest="debug",
                       action="store_true", default=False,
                       help="use debug ? (default: False)")
    args = parser.parse_args()

    log_dir = os.path.curdir
    if args.debug:
        # log_dir が空文字であれば、start_logger() 内部で、
        # log の出力先を sys.stderr に変更する。
        log_dir = ""

    start_logger(__file__, log_dir, logger.DEBUG)
    iat = IasapTkinter()
    iat.start()
