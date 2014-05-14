#!/usr/bin/env python3
from __future__ import print_function
__version__ = 1.0

from subprocess import Popen, DEVNULL
from useful.bench import Avg
import argparse
import errno
import shlex
import time
import sys
import gc
import os




class Bencher:
    def __init__(self, cmd, workers_num=1, spawn_limit=None, verbose=True):
        if isinstance(cmd, str):
            cmd = shlex.split(cmd)
        elif isinstance(cmd, list) and len(cmd)==1: #deal with situation like ["command args"]
            cmd = shlex.split(cmd[0])

        if spawn_limit is not None and spawn_limit < workers_num:
            raise Exception("spawn_limit < workers_num!")

        self.popens = {}
        self.cmd = cmd
        self.workers_num = workers_num
        self.verbose = verbose
        self.block_stdout = verbose
        self.spawn_limit = spawn_limit
        self.report_freq = 8


    def spawn_one(self):
        stdout = None if self.block_stdout else DEVNULL
        p = Popen(self.cmd, stdout=stdout)
        self.popens[p.pid] = p


    def wait_all(self):
        for p in self.popens.values():
            if self.verbose:
                print("[debug] waiting for", popen.pid)
            ret = p.wait()
            if self.verbose and ret:
                print("[error] Program returned with code", ret, file=sys.stderr)
        self.popens = {}


    #TODO: set on-exit hook
    def kill_all(self, signal):
        for p in self.popens:
            p.kill()
        self.popens = {}


    def run(self):
        avg = Avg(self.workers_num)

        #initial spawn of workers
        for x in range(self.workers_num):
            self.spawn_one()
            if self.spawn_limit is not None:
                self.spawn_limit -= 1
            #time.sleep(1)

        deads_count = 0
        total_time = -time.time()
        while True:
            try:
                pid, exitstatus, rusage = os.wait3(0)
            except OSError as e:
                if e.errno != errno.ECHILD:
                    raise
                return

            if exitstatus:
                sys.exit("process died with status %s" % exitstatus)

            cpu_total = rusage.ru_utime+rusage.ru_stime
            cpu_user  = rusage.ru_utime
            cpu_sys   = rusage.ru_stime
            print("{}: {total:.2f} {user:.2f} {sys:.2f}".format(pid, total=cpu_total, user=cpu_user, sys=cpu_sys))
            avg.append((cpu_total, cpu_user, cpu_sys))

            deads_count += 1
            if deads_count == self.report_freq:
                total_time += time.time()
                print("The execution of {num} processes took {time}s".format(num=self.report_freq, time=total_time))
                total_time = -time.time()
                deads_count = 0

            del self.popens[pid]

            if self.spawn_limit is not None and self.spawn_limit > 0:
                self.spawn_one()
                self.spawn_limit -= 1



if __name__ == '__main__':
    #CMD PARSER
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--repeat', type=int, default=1, help="repeat benchmark REPEAT times")
    parser.add_argument('-d', '--dry-run', type=int, default=False, help="run task once to prepopulate caches, etc")
    parser.add_argument('-a', '--affinity', type=int, default=0, help="mask that sets CPU affinity")
    parser.add_argument('-w', '--workers', type=int, default=1, help="run NUM tasks simultaneously")
    parser.add_argument('-s', '--spawn', type=int, default=None, help="limit the total number of spawned tasks")
    parser.add_argument('-m', '--mode', type=int, default=1, help="Mode: 1 - pipeline, 2 - bucket")
    parser.add_argument('-q', '--quiet', action='store_true', default=False, help="Reduce output")
    parser.add_argument('cmd', nargs="+", help="run CMD task")
    args = parser.parse_args()
    print(args)

    if args.affinity:
        exeutilz.set_affinity(args.affinity)

    if args.dry_run:
        print("dry run...", end="")
        b = Bencher(args.cmd, workers_num=args.workers, spawn_limit=args.spawn)
        b.run()
        b.wait_all()
        print("done")

    gc.disable()  # disable garbage collection to provide more accurate timings

    if args.mode == 1:
        b = Bencher(args.cmd, workers_num=args.workers, spawn_limit=args.spawn, verbose=not args.quiet)
        b.run()
    elif args.mode == 2:
        times = []
        total_time = -time.time()
        for x in range(args.repeat):
            print("======")
            t = -time.time()
            b = Bencher(args.cmd, num=args.num)
            b.run()
            b.wait_all()
            t += time.time()
            print("{:.1f}".format(t))
            times.append(t)
            #gc.collect()
        total_time += time.time()
        #REPORT
        print("avg={:.2f} min={:.2f} max={:.2f}".format(avg(times), min(times), max(times)))
        print("Total time: {:.2f}".format(total_time))
    else:
        sys.exit("Unknown mode %s" % args.mode)
