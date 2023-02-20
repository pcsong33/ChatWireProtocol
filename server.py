import time, socket, sys
import fnmatch
from threading import Thread
from collections import deque


class Client:
    def __init__(self, name, socket=None, addr=None):
        self.name = name
        self.socket = socket
        self.addr = addr
        self.msgs = []
        self.active = True
    
    def set_socket_addr(self, socket, addr):
        self.socket = socket
        self.addr = addr

    def disconnect(self):
        if self.socket:
            self.socket.close()
        self.socket = None
        self.addr = None
        self.active = False

    def queue_msg(self, sender, msg):
        self.msgs.append((sender, msg))

    def clear_msgs(self):
        self.msgs = []


clients = {}

# Send messages from server to client according to wire protocol
def send_message(c_socket, status, is_chat, msg):
    # msg_len = len(msg) # TODO: should we do anything w msg len?
    data = chr(status) + str(is_chat) + msg

    c_socket.sendall(data.encode())

# Threaded execution for each client
def on_new_client(c_socket, addr):
    try:
        c_name = None
        client = None

        while True:
            request = c_socket.recv(1024).decode() # TODO: fix to have header?
            op, msg = request.split('|', 1) if '|' in request else (request, '')
            op, msg = op.strip(), msg.strip()
            
            # Exit the chat
            if op == '0':
                break

            # Create an account
            elif op == '1':
                # Client is already logged in
                if client:
                    send_message(c_socket, 1, 0, f'Unable to create account: You are already logged in as {c_name}. Please exit (op code 0) and start a new client to log into a different account.')
                    continue
                # Username is already registered
                if msg in clients:
                    send_message(c_socket, 1, 0, 'Unable to create account: This username is already taken.')
                    continue
                # Username is blank
                if not msg:
                    send_message(c_socket, 1, 0, 'Unable to create account: Username cannot be blank.')
                    continue

                c_name = msg
                clients[c_name] = Client(c_name, c_socket, addr)
                client = clients[c_name]
                send_message(c_socket, 0, 0, f'Account created! Logged in as {c_name}.')
        
            # Log into existing account
            elif op == '2':
                # Client is already logged in
                if client:
                    send_message(c_socket, 1, 0, f'Unable to login: You are already logged in as {c_name}. Please exit (op code 0) and start a new client to log into a different account.')
                    continue
                # Username does not exist
                if msg not in clients:
                    send_message(c_socket, 1, 0, 'Unable to login: This username does not exist. If you would like to create a new account, use op code 1.')
                    continue
                # Client already active
                if clients[msg].active:
                    send_message(c_socket, 1, 0, 'Unable to login: This user is already connected to the server.')
                    continue
                
                c_name = msg
                client = clients[c_name]
                client.set_socket_addr(c_socket, addr)
                client.active = True
                send_message(c_socket, 0, 0, f'Logged in as {c_name}.')
                time.sleep(0.1)

                # Send any undelivered messages 
                for sender, msg in client.msgs:
                    send_message(client.socket, 0, 1, sender + '|' + msg)
                    print(f'{sender} sent {msg} to {c_name}')
                    time.sleep(0.1) # TODO: this is jank

                client.clear_msgs()

            # Send message to another client
            elif op == '3':
                # Must be logged in
                if not client:
                    send_message(c_socket, 1, 0, 'Must be logged in to perform this operation. Please login (op code 2) or create an account (op code 1).')
                    continue
                
                msg = msg.split('|', 1)

                # Validate parameters
                if len(msg) < 2:
                    send_message(c_socket, 1, 0, 'Not enough parameters specified. To send a message to another user, please type 3|[recipient]|[message].')
                    continue

                receiver = msg[0].strip()
                msg = msg[1].strip()

                if receiver not in clients:
                    send_message(c_socket, 1, 0, 'Recipient username cannot be found.')
                    continue
                if receiver == c_name:
                    send_message(c_socket, 1, 0, 'Cannot send messages to yourself.')
                    continue
                if msg == '':
                    send_message(c_socket, 1, 0, 'Cannot send blank message.')
                    continue
                
                # Send/Queue Message
                receiver_client = clients[receiver]

                if not receiver_client.socket:
                    receiver_client.queue_msg(c_name, msg) # TODO: lock things
                    send_message(c_socket, 0, 0, f'Message sent to {receiver}.')
                    print(f'{c_name} queued {msg} to {receiver}')
                else:
                    send_message(receiver_client.socket, 0, 1, c_name + '|' + msg)
                    send_message(c_socket, 0, 0, f'Message sent to {receiver}.')
                    print(f'{c_name} sent {msg} to {receiver}')

            # List accounts
            elif op == '4':
                accounts = '\n' 

                for key in fnmatch.filter(clients.keys(), msg if msg else '*'):
                    accounts += '- ' + key + '\n'

                send_message(c_socket, 0, 0, accounts)
                
            # Delete account
            elif op == '5':
                # Must be logged in
                if not client:
                    send_message(c_socket, 1, 0, 'Must be logged in to perform this operation. Please login (op code 2) or create an account (op code 1).')
                    continue

                clients.pop(c_name) # TODO: maybe stuff with locks here
                c_name = None
                client = None
            
            # Request was malformed
            else:
                send_message(c_socket, 1, 0, 'Invalid operation. Please input your request as [op code]|[params].')
        
        if (client):
            print(f'\n[-] {c_name} has left. Disconnecting client.\n')
            client.disconnect()

    except BrokenPipeError:
        if (client):
            print(f'\n[-] Connection with {c_name} has broken. Disconnecting client.\n')
            client.disconnect()

def main():
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

            print(f'\n[+] Connected to {addr[0]} ({addr[1]})\n')

            t = Thread(target=on_new_client, args=(c_socket, addr))
            t.start()

    except KeyboardInterrupt:
        print('\nServer closed with KeyboardInterrupt!')

        for c in clients:
            if clients[c].socket:
                clients[c].socket.close()

        s.close()


if __name__ == "__main__":
    main()
