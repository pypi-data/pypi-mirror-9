# Copyright 2011-2015 梅濁酒(umedoblock)

import re
import tkinter

class IasapTkinter(object):
    def __init__(self):
        self.root = tkinter.Tk()
        self.ss = b''
        self.root.option_add('*font', ('Ricty', 14))
        self.root.title('IasapTkinter')

        self.buffer = tkinter.StringVar()
        self.buffer.set(' ' * 80)

        # labelの設定
        lbl = tkinter.Label(self.root,
                            text='*** push any key ***RAISED',
                            background='#00ff00',
                            underline=1,
                            relief=tkinter.RAISED,
                            )
        lbl.pack(anchor=tkinter.W,
                 padx=5, pady=5,
                 ipadx=3, ipady=3,
                 side=tkinter.TOP,
                 )
        lbl = tkinter.Label(self.root,
                            text='*** push any key ****RIDGE',
                            background='gray',
                            underline=1,
                            borderwidth=3,
                            relief=tkinter.RIDGE,
                            )
        lbl.pack(anchor=tkinter.W,
                 padx=5, pady=5,
                 ipadx=3, ipady=3,
                 side=tkinter.TOP,
                 )
        lbl = tkinter.Label(self.root,
                            text='*** push any key ***SUNKEN',
                            background='#0000ff',
                            underline=1,
                            relief=tkinter.RAISED,
                            )
        lbl.pack(anchor=tkinter.W,
                 padx=5, pady=5,
                 ipadx=3, ipady=3,
                 side=tkinter.TOP,
                 )
        lbl = tkinter.Label(self.root,
                            text='*** push any key ***GROOVE',
                            background='red',
                            underline=1,
                            relief=tkinter.GROOVE,
                            )
        lbl.pack(anchor=tkinter.W,
                 padx=5, pady=5,
                 ipadx=3, ipady=3,
                 side=tkinter.TOP,
                 )

        a = tkinter.Label(self.root,
                          textvariable=self.buffer,
                          underline=0,
                          )
        self.a = a
        a.pack(anchor=tkinter.NW)
        a.bind('<Control-KeyPress>', self.ctrl_key)
        a.bind('<Any-KeyPress>', self.char_key)
        a.focus_set()

        line = ' ' * 80 + '\n'
        lbl = tkinter.Label(self.root,
                            text=line * 20,
                            borderwidth=1,
                            relief=tkinter.RIDGE,
                            )
        lbl.pack(anchor=tkinter.W,
                 padx=5, pady=5,
                 ipadx=3, ipady=3,
                 side=tkinter.TOP,
                 )

    def get_key(self, key):
        key = key.encode()
        if key == b'^C':
            self.root.quit()
        self.ss += key
        len_ss = len(self.ss)
      # msg = b'get_key() push key is ' + self.ss
      # msg = b' ' * 80 + b'\n' + self.ss
        padding = b' ' * (80 - len_ss)
        msg = self.ss + padding
        # print(help(self.buffer))
        self.a.config(underline=len_ss)
        self.buffer.set(msg)

    def char_key(self, event):
        char = event.char
        if not re.search('[-a-zA-Z0-9 &|]', char):
            return
        self.get_key(char)

    def ctrl_key(self, event):
        key = '^' + event.keysym.upper()
        self.get_key(key)

    def start(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass

if __name__ == '__main__':
    olt = IasapTkinter()
    olt.start()
