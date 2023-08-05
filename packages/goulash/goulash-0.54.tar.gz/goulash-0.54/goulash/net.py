""" goulash.net

    This is basically a bunch of neat stuff you can do with
    the socket library, and if I need it I dont want to look
    it up again.  I've also only tested it in linux, so YMMV
"""

import socket

def is_port_open(port, ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return True
    except:
        return False

def ipaddr_with_LAN(host = "gmail.com"):
    """ you need to make an outbound connection to get
        an ip-address on a particular interface.. so this
        function requires interwebs.

        this might actually be an address on the internet,
        more likely you are behind a router and this is
        a class C.
    """
    port = 80
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((host, port))
    result = s.getsockname()
    if len(result)==2:
        return result[0]

def ipaddr_hosts():
    """ on linux, uses /etc/hosts, returns something like this:

         ('cormac', ['localhost', 'testserver'], ['127.0.0.1'])
    """
    name, aliaslist, addresslist = socket.gethostbyname_ex(socket.gethostname())
    return name, aliaslist, addresslist

def ipaddr_basic():
    """ two different approaches just for reference purposes..
        these results are always the same for me, but ymmv depending
        on setup and platform..
    """
    x = []
    x.append(socket.gethostbyname(socket.gethostname()))
    x.append(socket.gethostbyname(socket.getfqdn()))
    return set(map(str, x))
