import socket
from gossip.util import packing

import time

port = 7001
ip_address = 'localhost'

def format(s):
    return [ord(i) for i in s]

if __name__ == "__main__":
    print('Sending 500')
    sock = socket.socket()
    sock.connect((ip_address, port))
    values = packing.pack_gossip_announce(0, 540, format('p2p is very cool!'))
    print(values)
    packing.send_msg(sock, values['code'], values['data'])
    sock.close()
    print('500 sent')
    #time.sleep(200)
