## An absolute minimal IRC client to post simple status messages to an IRC
## server. Note, this client is currently just hoping to get the communication
## right. It has been written without consulting the relevant protocol
## documentation.
import select
import socket


class IrcClient(object):

    def __init__(self, server, port, channel, nick):
        self._server  = server
        self._port    = port
        self._channel = channel
        self._nick    = nick
        self._socket  = None

    def _create_connection(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self._server, self._port))
        self._socket.setblocking(0)  # make non-blocking

    def _send(self, cmd):
        print "DO SEND: %s" % cmd
        self._socket.send(cmd + "\r\n")

    def _is_socket_ready(self, timeout):
        ready = select.select([self._socket], [], [], timeout)
        if ready[0]:
            return True
        else:
            return False

    def _recv_nonblocking(self):
        if self._is_socket_ready(0):
            return self._do_recv(0)

    def _recv_blocking(self):
        if self._is_socket_ready(10):
            return self._do_recv(10)

    def _do_recv(self, timeout):
        data = ""
        while self._is_socket_ready(timeout):
            result = self._socket.recv(4096)
            data += result
        return data.split("\r\n")

    def _wait_for_line_start_and_discard_rest(self, line_start):
        while True:
            if self._is_socket_ready(0.25):
                result = self._socket.recv(4096)
                lines = result.split("\r\n")
                for l in lines:
                    if l.startswith(line_start):
                        return

    def _handle_ping(self, data):
        """ Filter out PING requests and respond to them """
        if not data:
            return []
        result = []
        for l in data:
            if l.startswith("PING"):
                self._send("PONG %s" % l.split()[1])
            else:
                result.append(l)
        return result

    def _print_to_console(self, lines):
        for l in lines:
            print l

    def _do_handshake(self):
        self._send("NICK %s" % self._nick)
        self._send("USER %s %s %s :irc_client.py" % (self._nick,
                                                     self._nick, self._nick))
        self._wait_for_line_start_and_discard_rest(":%s MODE" % self._nick)

        self._send("JOIN %s" % self._channel)
        self._wait_for_line_start_and_discard_rest(":%s!"  % self._nick)

    def connect(self):
        self._create_connection()
        self._do_handshake()
        return True

    def send(self, msg):
        self._send("PRIVMSG %s :%s" % (self._channel, msg))

    def disconnect(self):
        self._send("QUIT")
        result = self._recv_nonblocking()
        result = self._handle_ping(result)
        # self._print_to_console(result)

# client = IrcClient("chat.freenode.net", 6666, "#som", "rebench-bot")
# if client.connect():
#     client.send("Hello World!")
#     client._channel = "smarr"
#     client.send("Hello World!")
#     client.disconnect()
#
# print "done"
