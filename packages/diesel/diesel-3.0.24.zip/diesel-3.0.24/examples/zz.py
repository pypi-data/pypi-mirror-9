import zmq

from diesel import quickstart, receive, sleep
from diesel.transports.zeromq import ZeroMQService


def handle_message(service):
    while True:
        msg = receive()
        print msg

quickstart(ZeroMQService(zmq.DEALER, handle_message, 7777))
