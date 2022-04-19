import socket
from threading import Thread
import time


class Peer:
    def __init__(self, ip: str, port: int, name: str) -> None:
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.r = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.r.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conn = None

        self.ip = ip
        self.port = port
        self.name = name
        self.is_active = True
        self.log_filename = f"{name}_{round(time.time())}.log"
        with open(self.log_filename, "w") as f:
            f.write(f"Started Socket at {time.strftime('%X %x %Z')} (EPOCH {round(time.time())})")

    def bind(self):
        try:
            self.r.bind((self.ip, self.port))
        except Exception as e:
            print("Error, could not bind socket to server " + self.ip + ":" + str(self.port))
            print(e)

    def connect(self, ip: str, port: int):
        try:
            self.s.connect((ip, port))
        except Exception as e:
            print("Error, could not establish connection with " + ip + ":" + str(port))
            print(e)

    def quit(self):
        try:
            print("--Disconnecting--")
            self.s.close()
            self.r.close()
            print("--Disconnected--")
        except:
            print("--quit failed--")
    
    def log_msg(self, msg_data):
        """Store messages between peers in db (TODO: Use actual DB, for now use log file)
        """
        with open(self.log_filename, "a") as f:
            f.write(msg_data)

    def send(self, data: str):
        try:
            self.log_msg(data)
            self.s.sendall(data.encode())
        except:
            print("Failed to send message")

    def receive(self, max_buffer_size = 5120):
        self.r.listen(1)
        self.is_active = True
        self.conn, addr = self.r.accept()
        print("Connected with " + str(addr[0]) + ":" + str(addr[1]))
        while self.is_active:
            try:
                data = self.conn.recv(max_buffer_size)  
                if("--DISCONNECT--" in data.decode()):
                    print("Peer is requesting to disconnect")
                    print("Press any key to disconnect")
                    self.is_active = False
                else:
                    print(data.decode())
            except ConnectionAbortedError:
                print("Peer has disconnected")
                self.is_active = False 
            except Exception as e:
                print("Error, could not receive message")
                raise(e)
        print("Receiver deactivated")

    def run_server(self, ip: str, port: int):
        print("Starting server")
        self.bind()
        try:
            Thread(target = self.receive).start()
        except Exception as e:
            print("Could not start thread")
            print(e)
        time.sleep(5)
        self.connect(ip, port)

        return
