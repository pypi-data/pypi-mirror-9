from __future__ import print_function
import time
import socket
import argparse
import netifaces

import requests

import spotimote_pb2


MULTICAST_GROUP = '224.242.224.224'
MULTICAST_PORT = 5116
MULTICAST_TIMEOUT = 5
COMMANDS = {}


def command(function):
    COMMANDS[function.__name__] = function


class Spotimote(object):
    def __init__(self, host=None, port=MULTICAST_PORT):
        self.host = host
        self.port = port

    def get_host(self):
        host = getattr(self, '_host', None)
        if not host:
            _, host, port = self.detect().next()
            self.host = host
            self.port = port

        return host

    def set_host(self, host):
        self._host = host

    def del_host(self):
        self._host = None

    host = property(get_host, set_host, del_host,
                    'The Spotimote host, will be automatically detected if not given')

    def _send_broadcast(self):
        broadcaster = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                                    socket.IPPROTO_UDP)
        broadcaster.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)

        broadcast_message = spotimote_pb2.BroadcastMsg()
        broadcast_message.port = MULTICAST_PORT
        for interface in netifaces.interfaces():
            addresses = netifaces.ifaddresses(interface)
            for address in addresses.get(netifaces.AF_INET, []):
                if 'netmask' in address:
                    broadcast_message.ip = address['addr']
                    broadcaster.sendto(broadcast_message.SerializeToString(),
                                       (MULTICAST_GROUP, MULTICAST_PORT))

    def detect(self):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            listener.settimeout(MULTICAST_TIMEOUT)
            listener.bind(('', MULTICAST_PORT))
            listener.listen(5)

            self._send_broadcast()

            start_time = time.time()
            while time.time() - start_time < MULTICAST_TIMEOUT:
                try:
                    connection, client_address = listener.accept()
                except socket.timeout:
                    break

                try:
                    data = connection.recv(1024)
                finally:
                    connection.close()

                broadcast_reply = spotimote_pb2.BroadcastReply()
                broadcast_reply.ParseFromString(data)
                yield broadcast_reply.name, broadcast_reply.ip,\
                      broadcast_reply.port
        finally:
            listener.close()

    def action(self, action_id):
        action = spotimote_pb2.ActionMsg()
        action.actionId = action_id
        requests.post('http://%s:5116/action' % self.host,
                      action.SerializeToString(), timeout=0.5)

    @command
    def play_pause(self):
        return self.action(spotimote_pb2.ActionMsg.ActionPlayPause)

    @command
    def next(self):
        return self.action(spotimote_pb2.ActionMsg.ActionNext)

    @command
    def prev(self):
        return self.action(spotimote_pb2.ActionMsg.ActionPrev)

    @command
    def shuffle(self):
        return self.action(spotimote_pb2.ActionMsg.ActionShuffle)

    @command
    def repeat(self):
        return self.action(spotimote_pb2.ActionMsg.ActionRepeat)

    @command
    def volume_up(self):
        return self.action(spotimote_pb2.ActionMsg.ActionVolumeUp)

    @command
    def volume_down(self):
        return self.action(spotimote_pb2.ActionMsg.ActionVolumeDown)


def main():
    parser = argparse.ArgumentParser(description='Control Spotimote')
    parser.add_argument('--host', help='The hostname or IP of the Spotimote '
                                       'server. If no host is given it will '
                                       'be detected automatically.')
    parser.add_argument('--port', default=MULTICAST_PORT,
                        help='The port of the Spotimote server')
    parser.add_argument('command', metavar='COMMAND', choices=COMMANDS.keys(),
                        help='Choose a command to execute (%s)' % ', '.join(
                            COMMANDS.keys()))

    try:
        args = parser.parse_args()
    except SystemExit:
        parser.print_help()
        raise

    spotimote = Spotimote()
    command = COMMANDS[args.command]

    if args.host:
        hosts = [('Commandline', args.host, args.port), ]
    else:
        print('Detecting hosts')
        hosts = list(spotimote.detect())
        if hosts:
            print('Got hosts:')
            for host in hosts:
                print(host)
        else:
            print('No hosts found')

    for _, host, port in hosts:
        print('Executing %s on %s:%s' % (args.command, host, port))
        spotimote.host = host
        spotimote.port = port
        command(spotimote)


if __name__ == '__main__':
    main()

