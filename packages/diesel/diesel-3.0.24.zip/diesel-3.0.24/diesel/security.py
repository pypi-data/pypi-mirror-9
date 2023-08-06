from OpenSSL import SSL
import traceback
import sys

def ssl_async_handshake(sock, hub, next):
    def shake():
        try:
            sock.do_handshake()
        except SSL.WantReadError:
            hub.disable_write(sock)
        except SSL.WantWriteError:
            hub.enable_write(sock)
        except SSL.WantX509LookupError:
            pass
        except Exception, e:
            hub.unregister(sock)
            next(e)
        else:
            hub.unregister(sock)
            next()
    hub.register(sock, shake, shake, shake)
    shake()
