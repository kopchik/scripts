#!/usr/bin/env python

PATTERNS = ["kliga-*", "kurdiani-*", "stuff-*"]

from glob import glob
from os import stat
from time import time

#from collections import namedtuple
#mystat = namedtuple("mystat", ["size", "ts"])
ERROR = 0
OK    = 1
WARNING = 2

MINUTES = 60
HOURS   = 60*MINUTES

def quotacheck():
  TODO


def backupcheck(g):
  log = []
  def warning(msg):
    log.append((WARNING, msg))
  def error(msg):
    log.append((ERROR, msg))

  files = glob(g)
  if not files:
    error("No backups for %s found" % g)
    return ERROR, log

  stats = ((f, stat(f)) for f in files)
  stats = [(f, s.st_size, s.st_ctime) for f,s in stats]
  stats.sort(key=lambda t: t[2], reverse=True)
  
  # check interval between backups and size changes
  prevf, prevs, prevts = stats[0]
  for f,s,ts in stats[1:]:
    ratio = s/prevs
    if not (0.9 < ratio < 1.1):
      error("too big difference in size" \
        "between %s and %s for %s and %s" % (prevs, s, prevf, f))
    interval = ts - prevts
    if interval > 25*3600:
      error("too big interval (%.1fh) between %f and %f" %(interval/HOURS, prevf, f))

  # check the last backup
  now = time()
  interval = now - ts  # where ts is the ts of the last backup
  if now - ts > 25*HOURS:
    error("for last backup was %.1h ago" % (g, interval))

  verdict = all(t[0] for r in log)
  return verdist, log


def fmtlog(p, verdict, log):
  print("for", p, "status is", {ERROR: "ERROR", OK: "OK", WARNING: "WARNING"}[verdict])
  for status, msg in log:
    print(status, msg)
  print()

if __name__ == '__main__':
  for p in PATTERNS:
    verdict, log = backupcheck(p)
    if verdict != OK:
      fmtlog(p, verdict, log)
