from diesel import Application, Loop, sleep
import time

def restart():
    print "I should restart"
    a = b

a = Application()
a.add_loop(Loop(restart), keep_alive=True)
a.run()
