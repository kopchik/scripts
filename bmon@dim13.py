#!/usr/bin/env python3.3
from __future__ import print_function, division

HOURS       = 3600
PATTERNS    = ["kliga-*", "kurdiani-*", "stuff-*"]
MAXCHANGE   = 0.14  # how much can consequent backups change (e.g., 0.1 for 10%)
MAXINTERVAL = 30*HOURS
QUOTAWARN   = 0.9  # warn when 90% of disk quota is used
MINBACKUPS  = 3
MAXBACKUPS  = 6
CHECKDEEP   = 2  # how many prev backups are checked for MAXCHANGE and MAXINTERVAL


from subprocess import check_output
from os import stat, unlink
from glob import glob
from time import time
from sys import exit

ERROR = 0
OK    = 1
WARNING = 2
statusmap = {ERROR: "ERROR", OK: "OK", WARNING: "WARNING"}


def quotacheck():
  status = OK, "quota is fine"
  output = check_output("quota").decode().splitlines()
  quotas = output[2:]  # strip headers
  for quota in quotas:
    try:
      #mnt, used, quota, hardlim, grace, files, flimit, fhardlim = quota.split()
      mnt, used, quota, hardlim, *rest = quota.split()
      used = used.strip('*')  # remove possible mark of overquota
    except Exception as err:
      return ERROR, "%s: %s" % (err, quota)
    percentage = int(used)/int(quota)
    if percentage > QUOTAWARN:
      status = ERROR, "quota exceeding for %s: %s used (quota=%s)" % (mnt, used, quota)
  return status


def backupcheck(g, maxbackups=-1):
  global CHECKDEEP

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
  stats = [(f, s.st_size, s.st_mtime) for f,s in stats]
  stats.sort(key=lambda t: t[2])

  # check number of backups
  if len(stats) < 2:
    error("OMG JUST ONE BACKUP!")
    return ERROR, log
  elif len(stats) < MINBACKUPS:
    error("too low number of backups")

  if CHECKDEEP < 2:
    CHECKDEEP = 2
    error("CHECKDEEP should be > 2")

  # check interval between backups and size changes
  prevf, prevs, prevts = stats[-CHECKDEEP]
  for f,size,tstamp in stats[-(CHECKDEEP-1):]:
    change = (size - prevs) / prevs
    if abs(change) > MAXCHANGE:
      error("backups changed for %.2f%% between %s and %s" % (change*100, prevf, f))
    interval = tstamp - prevts
    if interval < 0 or interval > MAXINTERVAL:
      error("too big interval (%.1fh) "  \
            "between %s and %s" %(interval/HOURS, prevf, f))
    prevf,prevs,prevts = f,size,tstamp

  # check the last backup
  _, _, tstamp = stats[-1]
  now = time()
  interval = now - tstamp  # where ts is the ts of the last backup
  if interval > 25*HOURS:
    error("%s: last backup (%s) was %.1fh ago" % (g, f, interval/HOURS))

  # prune old backups
  if maxbackups > 2:
    for fname, _, _ in stats[:-maxbackups]:
      try:
        unlink(fname)
      except Exception as err:
        error("cannot unlink %s: %s" % (fname, err))

  verdict = all(status for status,msg in log)
  return verdict, log


def fmtlog(p, verdict, log):
  print(p, ":", statusmap[verdict])
  for status, msg in log:
    print(statusmap[status],":", msg)
  print()


if __name__ == '__main__':
  status = OK, "everything is fine"
  badstatus = ERROR, "Bad exit status due to the previous errors"

  try:
    verdict, log = quotacheck()
    if verdict != OK:
      print(log)
      status = badstatus
  except Exception as err:
    status = badstatus
    print("quota check failed:", err)


  for p in PATTERNS:
    verdict, log = backupcheck(p, maxbackups=MAXBACKUPS)
    if verdict != OK:
      fmtlog(p, verdict, log)
      status = badstatus

  print(status[1])
  exit(0) if status != badstatus else exit(1)
