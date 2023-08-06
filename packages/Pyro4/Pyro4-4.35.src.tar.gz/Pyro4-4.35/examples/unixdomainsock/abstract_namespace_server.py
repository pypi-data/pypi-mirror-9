# this only works on Linux
# it uses the abstract namespace socket feature.

from __future__ import print_function
import Pyro4


class Thingy(object):
    def message(self, arg):
        print("Message received:", arg)
        return "Roger!"


d = Pyro4.Daemon(unixsocket="\0example_unix.sock")  # notice the 0-byte at the start
uri = d.register(Thingy(), "example.unixsock")
print("Server running, uri=", uri)
string_uri = str(uri)
print("Actually, the uri contains a 0-byte, make sure you copy this to the client:")
print(repr(string_uri))
d.requestLoop()
