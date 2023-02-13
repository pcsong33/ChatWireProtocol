import time, socket, sys
from threading import Thread
from collections import deque

class Client:
    def __init__(self, name, socket=None, addr=None):
        self.name = name
        self.socket = socket
        self.addr = addr
        self.msgs = []
    
    def set_socket_addr(self, socket, addr):
        self.socket = socket
        self.addr = addr

    def disconnect(self):
        self.socket.close()
        self.socket = None
        self.addr = None

    def queue_msg(self, sender, msg):
        self.msgs.append((sender, msg))

    def clear_msgs(self):
        self.msgs = []

clients = {}

# Threaded excution for each client
def on_new_client(c_socket, addr, c_name):
    print(f'\n[+] Connected to {c_name} at {addr[0]} ({addr[1]})\n')

    client = clients[c_name]

    # Send any undelivered messages 
    for sender, msg in client.msgs:
        client.socket.send((msg + '<' + sender).encode())
        print(f'{sender} sent {msg} to {c_name}')
        time.sleep(0.1)

    client.clear_msgs()

    while True:
        msg = c_socket.recv(1024).decode()

        # Client is exiting the chat
        if msg == '[e]':
            break
        # Client is deleting their account
        if msg == 'DELETE':
            clients.pop(c_name)
            break
        # Client wants list of all usernmes
        if msg == 'LIST':
            accounts = '' 

            for key in clients:
                accounts += '- ' + key + '\n'

            c_socket.send(accounts.encode())
            continue

        msg = msg.rsplit('>', 1)
        
        ## Handle Invalid Inputs
        if len(msg) < 2:
            c_socket.send('ERROR: No recipient specified. To send a message to a user, please input your message followed by \'>\' and the recipient\'s username.\n'.encode())
            continue

        receiver = msg[1].strip()
        msg = msg[0].strip()
        
        if receiver not in clients:
            c_socket.send('ERROR: Recipient username cannot be found.\n'.encode())
            continue
        if receiver == c_name:
            c_socket.send('ERROR: Cannot send messages to yourself.\n'.encode())
            continue
        if msg == '':
            c_socket.send('ERROR: Cannot send blank message.\n'.encode())
            continue

        ## Send/Queue Message
        receiver_client = clients[receiver]

        if not receiver_client.socket:
            receiver_client.queue_msg(c_name, msg)
            print(f'{c_name} queued {msg} to {receiver}')
        else:
            receiver_client.socket.send((msg + '<' + c_name).encode())
            print(f'{c_name} sent {msg} to {receiver}')

    print(f'\n[-] {c_name} has left. Disconnecting client.\n')
    client.disconnect()

try:
    s = socket.socket()
    host = socket.gethostname()
    # host = "dhcp-10-250-203-22.harvard.edu"
    ip = socket.gethostbyname(host)
    port = 1538
    print(f'\n{host} ({ip})')

    s.bind((host, port))
    print('\nServer started!')

    s.listen(5)
    print('\nWaiting for incoming connections...')

    while True:
        c_socket, addr = s.accept()
        c_name = c_socket.recv(1024).decode().strip()

        # Client already exists
        if c_name in clients: # TODO: handle login when already connected
            clients[c_name].set_socket_addr(c_socket, addr)
        # New user
        else:
            clients[c_name] = Client(c_name, c_socket, addr)

        t = Thread(target=on_new_client, args=(c_socket, addr, c_name))
        t.start()

except KeyboardInterrupt:
    # TODO: close all client sockets too
    print('\nServer closed with KeyboardInterrupt!')
    s.close()