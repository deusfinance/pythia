import socket
from gossip.util import packing, message

__author__ = 'Anselm Binninger, Ralph Schaumann, Thomas Maier'

try:
    sock = socket.socket()
    sock.connect(('localhost', 6001))
    while True:
        values = packing.receive_msg(sock)
        message_object = message.GOSSIP_MESSAGE_TYPES.get(values['code'], message.MessageOther)
        print(values)
        if 500 <= values['code'] < 520:
            print(message_object(values['message']))
        else:
            print(values)
        #sock.close()
except Exception as e:
    import traceback;traceback.print_exc()
    print('%s' % e)
