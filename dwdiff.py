#!/usr/bin/env python3
import sys
import os


LEFT  = sys.argv[-2]
RIGHT = sys.argv[-1]

cmd = ["dwdiff", LEFT, RIGHT]
os.execvp(cmd[0], cmd)
