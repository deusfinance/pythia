import socket
from gossip.util import packing, message
import threading
import redis
import time
from gossip.gossip_main import main as run_gossip
import node_utils
import os, traceback
from utils import cmd_options
from env import load_env
import sources


def bytes_to_string(l):
    return "".join(map(chr, l))


def string_to_bytes(s):
    return [ord(i) for i in s]


class GossipRunner(threading.Thread):
    def run(self):
        print("Starting gossip")
        run_gossip()


class Sender(threading.Thread):

    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock
        self.redis_con = redis.Redis(host=os.getenv("REDIS_HOST"))
        self.queue = os.getenv("REDIS_QUEUE")

    def run(self):
        print("Starting Sender ...")
        while True:
            source, data = self.redis_con.blpop(self.queue)
            self.handle_message(bytes_to_string(data))

    def handle_message(self, data):
        values = packing.pack_gossip_announce(0, 540, string_to_bytes(data))
        packing.send_msg(self.sock, values['code'], values['data'])
        #sock.close()


class Receiver(threading.Thread):

    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock

    def run(self):
        print("Starting Receiver ...")
        while True:
            values = packing.receive_msg(sock)
            try:
                self.handle_message(values)
            except:
                traceback.print_exc()

    def handle_message(self, values):
        message_object = message.GOSSIP_MESSAGE_TYPES.get(
            values['code'], 
            message.MessageGossipNotification
        )
        msg = message_object(values['message'])
        json_str = bytes_to_string(msg.msg)
        node_utils.process_message(json_str)


if __name__ == "__main__":
    options = cmd_options.read()

    if not options.node:
        load_env()
        gossip_runner = GossipRunner()
        gossip_runner.daemon = True
        gossip_runner.start()

        time.sleep(10)

        sock = socket.socket()
        sock.connect(('localhost', 7001))

        values = packing.pack_gossip_notify(540)
        packing.send_msg(sock, values['code'], values['data'])

        receiver = Receiver(sock)
        receiver.daemon = True
        receiver.start()

        sender = Sender(sock)
        sender.daemon = True
        sender.start()

        sources.init_services()

        receiver.join()
        sender.join()
    else:
        load_env(".env.%s" % options.node)

        sock = socket.socket()
        sock.connect(('localhost', 7001))

        values = packing.pack_gossip_notify(540)
        packing.send_msg(sock, values['code'], values['data'])

        receiver = Receiver(sock)
        receiver.daemon = True
        receiver.start()

        receiver.join()
