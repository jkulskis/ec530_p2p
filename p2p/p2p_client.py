from p2p import Peer


if __name__ == "__main__":
    peer_2 = Peer(
        server_port=3000,
        debug=True,
        name="Test Peer 2",
        server_host="127.0.0.2",
    )
    peer_2.connectandsend("127.0.0.1", 3000, "std", "Hello Reed", pid=0, waitreply=True)