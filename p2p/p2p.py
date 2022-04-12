# Following tutorial: https://cs.berry.edu/~nhamid/p2p/
import socket
import threading
import traceback
import time

class Peer:
    def __init__(
        self,
        server_port: int,
        debug: bool = False,
        name: str = None,
        server_host: str = None,
    ):
        self.max_peers = 0  # 0 is for unlimited peers
        self.server_port = server_port
        if server_host is not None:
            self.server_host = server_host
        else:
            # find local machine's IP address by connecting to the internet
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("www.google.com", 80))
            self.server_host = s.getsockname()[0]
            s.close()

        self.name = (
            name if name is not None else f"{self.server_host}:{self.server_port}"
        )

        self.peerlock = threading.Lock()  # ensure proper access to
        # peers list (maybe better to use
        # threading.RLock (reentrant))
        self.peers = {}  # peer_id ==> (host, port) mapping
        self.shutdown = False  # used to stop the main loop
        self.debug = debug

        self.router = None

    def __debug(self, msg: str):
        if self.debug:
            print(msg)

    def handle_peer(self, client_sock: socket.socket):
        """
        handle_peer( new socket connection ) -> ()

        Dispatches messages from the socket connection
        """

        self.__debug(f"New child {threading.currentThread().getName()}")
        self.__debug(f"Connected {client_sock.getpeername()}")

        host, port = client_sock.getpeername()
        peer_conn = PeerConnection(None, host, port, client_sock, debug=False)

        try:
            msg_type, msg_data = peer_conn.recvdata()
            if msg_type:
                msg_type = msg_type.upper()
            self.__debug(f"Handling peer msg: {msg_type}: {msg_data}")
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()

        self.__debug(f"Disconnecting {client_sock.getpeername()}")
        peer_conn.close()

    def addpeer(self, peer_id, host, port: int):
        """Adds a peer name and host:port mapping to the known list of peers."""
        if peer_id not in self.peers and (
            self.max_peers == 0 or len(self.peers) < self.max_peers
        ):
            self.peers[peer_id] = (host, port)
            return True
        else:
            return False

    def get_peer(self, peer_id):
        """Returns the (host, port) tuple for the given peer name"""
        assert peer_id in self.peers  # maybe make this just a return NULL?
        return self.peers[peer_id]

    def remove_peer(self, peer_id):
        """Removes peer information from the known list of peers."""
        if peer_id in self.peers:
            del self.peers[peer_id]

    def get_peer_ids(self):
        """Return a list of all known peer id's."""
        return self.peers.keys()

    def max_peers_reached(self):
        """Returns whether the maximum limit of names has been added to the
        list of known peers. Always returns True if max_peers is set to
        0.

        """
        assert self.max_peers == 0 or len(self.peers) <= self.max_peers
        return self.max_peers > 0 and len(self.peers) == self.max_peers

    def make_server_socket(self, port, backlog=5):
        """Constructs and prepares a server socket listening on the given
        port.

        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", port))
        s.listen(backlog)
        return s

    def sendtopeer(self, peer_id, msg_type, msg_data, waitreply=True):
        """
        sendtopeer( peer id, message type, message data, wait for a reply )
        -> [ ( reply type, reply data ), ... ]

        Send a message to the identified peer. In order to decide how to
        send the message, the router handler for this peer will be called.
        If no router function has been registered, it will not work. The
        router function should provide the next immediate peer to whom the
        message should be forwarded. The peer's reply, if it is expected,
        will be returned.

        Returns None if the message could not be routed.
        """

        if self.router:
            nextpid, host, port = self.router(peer_id)
        if not self.router or not nextpid:
            self.__debug(f"Unable to route {msg_type} to {peer_id}")
            return None
        # host,port = self.peers[nextpid]
        return self.connectandsend(
            host, port, msg_type, msg_data, pid=nextpid, waitreply=waitreply
        )

    def connectandsend(self, host, port, msg_type, msg_data, pid=None, waitreply=True):
        """
        connectandsend( host, port, message type, message data, peer id,
        wait for a reply ) -> [ ( reply type, reply data ), ... ]

        Connects and sends a message to the specified host:port. The host's
        reply, if expected, will be returned as a list of tuples.

        """
        msgreply = []
        try:
            peerconn = PeerConnection(pid, host, port, debug=self.debug)
            peerconn.send_data(msg_type, msg_data)
            self.__debug(f"Sent {pid}: {msg_type}")

            if waitreply:
                onereply = peerconn.recvdata()
                while onereply != (None, None):
                    msgreply.append(onereply)
                    self.__debug(f"Got reply {pid}: {msgreply}")
                    onereply = peerconn.recvdata()
                peerconn.close()
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()

        return msgreply

    def checklivepeers(self):
        """Attempts to ping all currently known peers in order to ensure that
        they are still active. Removes any from the peer list that do
        not reply. This function can be used as a simple stabilizer.

        """
        todelete = []
        for pid in self.peers:
            isconnected = False
            try:
                self.__debug("Check live %s" % pid)
                host, port = self.peers[pid]
                peerconn = PeerConnection(pid, host, port, debug=self.debug)
                peerconn.send_data("PING", "")
                isconnected = True
            except:
                todelete.append(pid)
            if isconnected:
                peerconn.close()

        self.peerlock.acquire()
        try:
            for pid in todelete:
                if pid in self.peers:
                    del self.peers[pid]
        finally:
            self.peerlock.release()

    def mainloop(self):
        s = self.make_server_socket(self.server_port)
        s.settimeout(5)
        self.__debug(
            f"Server started: {self.name} ({self.server_host}:{self.server_port})"
        )

        while not self.shutdown:
            try:
                self.__debug("Listening for connections...")
                client_sock, clientaddr = s.accept()
                client_sock.settimeout(None)

                t = threading.Thread(target=self.handle_peer, args=[client_sock])
                t.start()
            except KeyboardInterrupt:
                print("KeyboardInterrupt: stopping mainloop")
                self.shutdown = True
                continue
            except:
                if self.debug:
                    traceback.print_exc()
                    continue
        self.__debug("Main loop exiting")

        s.close()


class PeerConnection:
    def __init__(self, peer_id, host, port, sock=None, debug=False):
        # any exceptions thrown upwards

        self.id = peer_id
        self.debug = debug

        if not sock:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((host, int(port)))
        else:
            self.s = sock

        self.sd = self.s.makefile("rwb", 0)

    def __debug(self, msg):
        if self.debug:
            print(msg)

    def send_data(self, msg_type, msg_data):
        """
        send_data( message type, message data ) -> boolean status

        Send a message through a peer connection. Returns True on success
        or False if there was an error.
        """

        try:
            msg = f"{msg_type}\r\n{msg_data}"
            self.sd.write(msg.encode())
            self.sd.flush()
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()
            return False
        return True

    def recvdata(self):
        """
        recvdata() -> (msg_type, msg_data)

        Receive a message from a peer connection. Returns (None, None)
        if there was any error.
        """
        msg_type, msg = None, None
        try:
            data = self.sd.read(2048)
            if not data:
                return (None, None)
            msg_type, msg = data.decode().split("\r\n")
        except KeyboardInterrupt:
            raise
        except:
            if self.debug:
                traceback.print_exc()
            return (None, None)

        return (msg_type, msg)

    def close(self):
        """
        close()

        Close the peer connection. The send and recv methods will not work
        after this call.
        """

        self.s.close()
        self.s = None
        self.sd = None

    def __repr__(self):
        return f"|{peer_id}|"


if __name__ == "__main__":
    peer = Peer(
        server_port=3000,
        debug=True,
        name="Test Peer 1",
        server_host="127.0.0.1",
    )
    peer.mainloop()
