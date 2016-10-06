#!/usr/bin/env python3

import daemon
from syslog import syslog
from time import sleep
import os
import shlex
import subprocess

def run(cmd):
  syslog("running %s" % cmd)
  try:
    return subprocess.check_output(cmd, shell=True).decode().strip()
  except subprocess.CalledProcessError:
    syslog("failed to exec %s" % cmd)
    return False


def setup():
  os.environ["DISPLAY"] = ":0.0"
  run("setxkbmap -option grp:shift_caps_switch,caps:ctrl_modifier")
  run("xset r rate 200 60")
  run("xset m 0")
  for line in run("xinput list | grep -i mouse").splitlines():
    for tok in line.split():
      if tok.startswith('id='):
        dev_id = tok.split('=')[1]
        run("xinput set-ptr-feedback %s 4 1 1" % dev_id)



if __name__ == '__main__':
  os.closerange(0, 65535)
  pid = os.fork()
  if not pid:
    pid = os.fork()  # double fork
    if not pid:
      with open("/sys/fs/cgroup/cpu/tasks", "a+") as fd:
        fd.write(str(os.getpid()))
      sleep(3)
      syslog("I'm alive!")
      setup()
  sleep(0.1)  # get forked process chance to change cgroup
  print("background process forked, releasing shell...")
