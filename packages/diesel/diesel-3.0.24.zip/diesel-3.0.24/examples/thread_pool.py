from diesel import quickstart, sleep, quickstop
from diesel.util.pool import ThreadPool
import random

def handle_it(i):
    print 'S', i
    sleep(random.random())
    print 'E', i

def c():
    for x in xrange(0, 20):
        yield x

make_it = c().next

def stop_it():
    quickstop()

threads = ThreadPool(10, handle_it, make_it, stop_it)

quickstart(threads)
