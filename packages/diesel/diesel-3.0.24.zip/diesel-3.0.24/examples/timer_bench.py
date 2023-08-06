"""A benchmark for diesel's internal timers.

Try something like:

    $ python examples/timer_bench.py 10
    $ python examples/timer_bench.py 100
    $ python examples/timer_bench.py 1000

The script will output the total time to run with the given number of
producer/consumer pairs and a sample of CPU time while the benchmark was
running.

"""
import os
import subprocess
import sys
import time

import diesel
from diesel.util.event import Countdown
from diesel.util.queue import Queue

OPERATIONS = 60
cpustats = []


def producer(q):
    for i in xrange(OPERATIONS):
        diesel.sleep(0.5)
        q.put(i)

def consumer(q, done):
    for i in xrange(OPERATIONS):
        evt, data = diesel.first(waits=[q], sleep=10000)
        if evt == "sleep":
            print "sleep was triggered!"
            break
    done.tick()

def pair(done):
    q = Queue()
    diesel.fork(producer, q)
    diesel.fork(consumer, q, done)

def track_cpu_stats():
    pid = os.getpid()
    def append_stats():
        rawstats = subprocess.Popen(['ps -p %d -f' % pid], shell=True, stdout=subprocess.PIPE).communicate()[0]
        header, data = rawstats.split('\n', 1)
        procstats = [d for d in data.split(' ') if d]
        cpustats.append(int(procstats[3]))
    while True:
        diesel.sleep(1)
        diesel.thread(append_stats)

def main():
    diesel.fork(track_cpu_stats)
    actor_pairs = int(sys.argv[1])
    done = Countdown(actor_pairs)
    for i in xrange(actor_pairs):
        pair(done)
    start = time.time()
    done.wait()
    print "done in %.2f secs" % (time.time() - start)
    diesel.sleep(1)
    diesel.quickstop()

if __name__ == '__main__':
    diesel.set_log_level(diesel.loglevels.ERROR)
    diesel.quickstart(main)
    print cpustats
