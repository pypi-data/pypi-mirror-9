# Copyright 2011-2015 梅濁酒(umedoblock)

import sys
import time
import unittest
import threading
import os
import tempfile

from iasap_curses import *

class TestIasapCurses(unittest.TestCase):
    def setUp(self):
        self.f = tempfile.TemporaryFile(dir='.')
        stdin_fileno = sys.stdin.fileno()
        os.dup2(self.f.fileno(), stdin_fileno)

    def write(self, ss):
        self.f.write(ss)
        self.f.seek(-len(ss), os.SEEK_CUR)

    def tearDown(self):
        stdin_fileno = sys.stdin.fileno()
        os.dup2(stdin_fileno, self.f.fileno())
        self.f.close()

    def test_start_and_end(self):
        ocs = IasapCurses()
        self.write(b'abc')
        ocs.run(CursesLine)

#   infinite loop
#   def test_over_write(self):
#       ocs = IasapCurses()
#       self.write(b'abc')
#       ocs.run(CursesLine)

if __name__ == '__main__':
    unittest.main()
