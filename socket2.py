from sockets import Peer

def main():
    name = input("Enter your display name: ")
    p = Peer('localhost', 50001, name)
    p.run_server('localhost', 50000)

if __name__ == "__main__":
    main()