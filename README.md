# Peer to Peer connections

EC530 Hackathon

## Project Overview

This project was part of a hackathon competition among the class. The goal was to make a platform for users to chat throug p2p connections. Users should be able to connect and talk to any user on the network and synchromise messages if any of the peers went offline. No data is stored on a centralized server and all local data is stored securily on the clients. We use a centralized "phonebook" server where users can see which peers are currently online for easy access to their information (ip and port number), however all of the packet sending is decentralized

## Running the code

To use our platform, you must download the source code and install all the dependencies from the `requirements.txt`. Once this is done, run the `main.py` code on your terminal. To be able to connect to another peer, they must also be running the `main.py` function at the same time and input your username when prompted. 
Since our phonebook server is not currently up, the app will not work without consulting the team. 

## Main function

The main function prompts the user for information before setting up any cnnections. 

- Unique Username
- Port number
- Password

It then creates a peer instance for the user and adds them to the network of active users.

The user can then input the username of the person they would like to chat to. The function will then make a get request to check if that user is currently online or not. If they are, the peers will connect and will be able to send messages to each other until one of them sends "--DISCONNECT--". If the other peer is not currently online, the user can still send them messages which will be saved and sent later once both of the users are back online. Once a user disconnects from a chat with a peer, they are asked if they would like to chat with someone else or quit the platform. 

## `Peer` Class

### Constructor

```python
    def __init__(self, ip: str, port: int, name: str) -> None:
```

The constructor takes as input your device's ip number, a port number, and your username. 
In addition, it creates your client and server sockets for sending and receiving messages, and creates a file to log all your messages for future reference. 

### Functions

- `def bind(self):`
    - This function binds your server socket to your ip and port number.

- `def connect(self, ip: str, port: int):`
    - This function tries to connect your client socket to the given ip/port peer server socket. 

- `def quit():`
    - This function will close both your client and server sockets once you are done using the platform.

- `def log_msg(self, msg_data):`
    - This function logs your messages with a timestamp to the log file configured in the constructor.

- `def send(self, data: str):`
    - This function tries to send the message `data` to connected socket.

- `def receive(self, max_buffer_size = 5120):`
    - This function tries to get the messages sent to you by your peer. 
    - It lisens for one connection at a time and keeps receiving messages until either of the peers disconnects. 
    - The `max_buffer_size` parameter is used to limit the number of bytes that can be sent in one message.

- `def run_server(self, ip: str, port: int):`
    - This function tries to create a new thread with the receive function as a target. This is to make receiving and sending messages concurrent and not interfere with each other. 
    - It also calls the connect function to create the sending ocnnection to the other peer.


## Phonebook Server

### Endpoints:

- `/peers/<string:username>`\
Create, delete (your own), and read users from the phonebook using their username.

    - POST user example:
    ```python
    data = { 
        'IP': '127.0.0.1:5000', 
        'port': 80,
        'password': 'password'
    }
    response = requests.post(BASE + 'peers/*username*', json = data)
    ``` 

    - GET user example:
    ```python
    response = requests.get(BASE + 'peers/*username*')
    ```

    - DELETE (your own) user example:
    ```python
    data = { 
        'password': 'password'
    }
    response = requests.delete(BASE + 'peers/*username*', json = data)
    ```

- `/peers/`
    - GET (all) users example:
    ``` python
    response = requests.get(BASE + 'peers/')
    ```

