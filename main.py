from re import T
import socket
from sockets import Peer
from threading import Thread
import time
import requests

BASE = 'http://127.0.0.1:5000/'

def main():
    # hostname = socket.gethostname()
    # local_ip = socket.gethostbyname(hostname)
    local_ip = "localhost"
    print("Welcome to our p2p platform")
    username = input("Please choose a unique username: ")
    port = int(input("Type in your desired port number: "))
    pw = input("Please type a strong password: ")
    data = { 
        'IP': local_ip, 
        'port': port,
        'password': pw
    }    

    print('Posting ' + username)
    response = requests.post(BASE + 'peers/' + username, json = data)
    # print(handle_request(response))

    while(response.status_code != 201):
        print("Post failed. Invalid username")
        username = input("Please choose a unique username: ")
        port = int(input("Type in your desired port number: "))
        pw = input("Please type a strong password: ")
        data = { 
            'IP': local_ip, 
            'port': port,
            'password': pw
        }    
        print('Posting ' + username)
        response = requests.post(BASE + 'peers/' + username, json = data)
    
    print("User successfully added to network")
    curr = Peer(local_ip, port, username)

    while(True):
        peer = input("Please enter the username of the person you want to chat with: ")

        print("Getting peer " + peer)
        response = requests.get(BASE + 'peers/' + peer)
        b = 'y'
        while(response.status_code == 404):
            print("Failed to get peer " + peer + ". This user is not currently active")
            b = input("Would you like to try a new user? Type 'y' or 'n'. You can still message this person while they are offline: ")
            if(b == 'y'):
                peer = input("Please enter the username of the person you want to chat with: ")
                print("Getting peer " + peer)
                response = requests.get(BASE + 'peers/' + peer)
            else:
                break
        

        # run the server here and send unsent messages
        if(b == 'y'): 
            curr.run_server(response.json()['IP'], response.json()['port'])
            try:
                f = open("unsent.txt", "r+")
                ls = f.readlines()
                f.seek(0)
                f.truncate()
                f.close()
                fw = open("unsent.txt", "a")
                for x in ls:
                    l = x.split()
                    if(l[-3] == peer):
                        curr.send(username + " - " + " ".join(l[0:-3]))
                    else:
                        fw.write(x)
                fw.close()
            except Exception as e:
                print("This shit failed for some reason")
                raise(e)

        print("You are now chatting with " + peer)  
        print("Type --DISCONNECT-- to quit this chat")
        message = input("Start your conversation: ")
        while(message != "--DISCONNECT--" and curr.is_active):
            if(b == 'n'): # Meaning peer is offline
                f = open("unsent.txt", 'a')
                f.write(message + " " + peer + " EPOCH " + str(int(time.time())) + "\n")
                f.close()
                message = input()
                continue

            curr.send(username + " - " + message)  
            message = input() 

        if message == "--DISCONNECT--" and b == 'y':
            curr.send(message)
            curr.is_active = False
            try:
                curr.conn.close()
            except:
                print("Hellojhfkfjgg,j")
            print("Please wait for peer to disconnect")
        
        b = input("Would you like to chat with someone new? Type 'y' or 'n': ")
        if(b != 'y'):
            break
        curr.is_active = True
        
    curr.quit()
    print("Thank you for using our p2p platform. See you soon!")
    print("Deleting user " + username)
    response = requests.delete(BASE + 'peers/' + username, json = data)

    return

if __name__ == "__main__":
    main()
