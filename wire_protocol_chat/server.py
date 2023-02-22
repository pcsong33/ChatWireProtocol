import socket
import fnmatch
import threading

'''
A User object represents an account that is created. It keeps track of the username, whether the user 
is active or not, the client socket logged into the account, and the undelivered messages to the user.
'''
class User:
    def __init__(self, name, socket=None, addr=None):
        self.name = name
        self.socket = socket
        self.addr = addr
        self.active = True
        self.msgs = []
        self.lock = threading.Lock()
    
    # For setting the socket and address of the user when a client logs in.
    def set_socket_addr(self, socket, addr):
        self.socket = socket
        self.addr = addr

    # When the client logged in as the user disconnects
    def disconnect(self):
        if self.socket:
            self.socket.close()
        self.socket = None
        self.addr = None
        self.active = False

    # Used by another client to queue a message to this user if they are inactive.
    # Multiple clients on diff threads may attempt to queue msgs simultaneously, so a lock is needed.
    def queue_msg(self, sender, msg):
        with self.lock:
            self.msgs.append((sender, msg))

    # For clearing the queue of messages after they have been sent.
    def clear_msgs(self):
        self.msgs = []

'''
The Server object accepts connections from multiple clients, and listens to client requests in order 
to respond and pass chat messages between clients. It keeps a global dictionary of all User objects.
'''
class Server:
    def __init__(self, port=1538):
        self.port = port
        self.s = socket.socket()
        self.host = socket.gethostname()
        self.ip = socket.gethostbyname(self.host)
        self.users = {}
        self.lock = threading.Lock()

    # Package and send messages from server to client according to wire protocol
    def send_msg_to_client(self, c_socket, status, is_chat, msg):
        msg_len = len(msg)
        data = chr(msg_len) + chr(status) + str(is_chat) + msg
        c_socket.sendall(data.encode())
            
    # Op 1 - Create Account
    def create_account(self, client, c_socket, c_name, addr, name):
        # Client is already logged in
        if client:
            self.send_msg_to_client(c_socket, 1, 0, f'Unable to create account: You are already logged in as {c_name}. Please exit and start a new client to log into a different account.')
            return 1
        
        with self.lock:
            # Username is already registered
            if name in self.users:
                self.send_msg_to_client(c_socket, 1, 0, 'Unable to create account: This username is already taken.')
                return 1
            
            # Register user - create new User object
            self.users[name] = User(name, c_socket, addr)

        self.send_msg_to_client(c_socket, 0, 0, f'Account created! Logged in as {name}.')
        print(f'{name} has created an account.')
        return 0

    # Op 2 - Login
    def login(self, client, c_socket, c_name, addr, name):
        # Client is already logged in
        if client:
            self.send_msg_to_client(c_socket, 1, 0, f'Unable to login: You are already logged in as {c_name}. Please exit  and start a new client to log into a different account.')
            return 1

        # Username does not exist
        if name not in self.users:
            self.send_msg_to_client(c_socket, 1, 0, 'Unable to login: This username does not exist. If you would like to use this username, please create a new account.')
            return 1

        with self.users[name].lock:
            # User already active
            if self.users[name].active:
                self.send_msg_to_client(c_socket, 1, 0, 'Unable to login: This user is already connected to the server.')
                return 1
            
            self.users[name].set_socket_addr(c_socket, addr)
            self.users[name].active = True

        self.send_msg_to_client(c_socket, 0, 0, f'Logged in as {name}.')
        print(f'{name} is logged in.')
        return 0

    # Upon login, send messages user missed
    def send_queued_chats(self, client, c_socket, c_name):
        total_msgs = len(client.msgs)

        # No new messages
        if (total_msgs == 0):
            self.send_msg_to_client(c_socket, 2, 0, 'No new messages since you\'ve been gone.')
            return 0

        for sender, queued_msg in client.msgs:
            # Check if queued message is from a deleted user, and display name with [deleted] if so
            deleted_flag = ""
            if sender not in self.users:
                deleted_flag = " [deleted]"

            self.send_msg_to_client(c_socket, 0, 1, sender + deleted_flag + '|' + queued_msg)
            print(f'{sender} sent {queued_msg} to {c_name}')

        self.send_msg_to_client(c_socket, 2, 0, f'You have {total_msgs} missed messages above.')
        client.clear_msgs()

    # Op 3 - Send chat messages from client to client
    def send_chat(self, client, c_socket, c_name, receiver, msg):
        # Must be logged in
        if not client:
            self.send_msg_to_client(c_socket, 1, 0, 'Must be logged in to perform this operation. Please login or create an account.')
            return 1

        # Validate recipient
        if receiver not in self.users:
            self.send_msg_to_client(c_socket, 1, 0, 'Recipient username cannot be found.')
            return 1
        if receiver == c_name:
            self.send_msg_to_client(c_socket, 1, 0, 'Cannot send messages to yourself.')
            return 1
        
        receiver_client = self.users[receiver]

        # Queue message if receiver inactive
        if not receiver_client.active:
            receiver_client.queue_msg(c_name, msg)
            self.send_msg_to_client(c_socket, 0, 0, f'Message sent to {receiver}.')
            print(f'{c_name} queued {msg} to {receiver}')
            return 0

        # Send message on demand if active
        try:
            self.send_msg_to_client(receiver_client.socket, 0, 1, c_name + '|' + msg)
            self.send_msg_to_client(c_socket, 0, 0, f'Message sent to {receiver}.')
            print(f'{c_name} sent {msg} to {receiver}')
            return 0
        except BrokenPipeError:
            self.send_msg_to_client(c_socket, 1, 0, f'Message could not be sent to {receiver}. Please try again.')
            print(f'\n[-] Connection with {receiver_client.name} has broken. Disconnecting client.\n')
            receiver_client.disconnect()
            return 1


    # Threaded execution for each client
    def on_new_client(self, c_socket, addr):
        try:
            c_name = None
            client = None

            while True:
                request = c_socket.recv(1024).decode()

                # Unpack data according to wire protocol
                op, msg = request.split('|', 1) if '|' in request else (request, '')
                op, msg = op.strip(), msg.strip()

                # Create an account
                if op == '1':
                    status = self.create_account(client, c_socket, c_name, addr, msg)

                    # Successfully created account
                    if status == 0:
                        c_name = msg
                        client = self.users[c_name]
            
                # Log into existing account
                elif op == '2':
                    status = self.login(client, c_socket, c_name, addr, msg)

                    # Successfully logged in
                    if status == 0:
                        c_name = msg
                        client = self.users[c_name]

                        # Send any undelivered messages 
                        self.send_queued_chats(client, c_socket, c_name)

                # Send message to another client
                elif op == '3':
                    msg = msg.split('|', 1)
                    receiver, msg = msg[0].strip(), msg[1].strip()
                    self.send_chat(client, c_socket, c_name, receiver, msg)

                # List accounts
                elif op == '4':
                    accounts = '\n' 

                    for key in fnmatch.filter(self.users.keys(), msg if msg else '*'):
                        accounts += '- ' + key + '\n'

                    self.send_msg_to_client(c_socket, 0, 0, accounts)
                    
                # Delete account
                elif op == '5':
                    # Must be logged in
                    if not client:
                        self.send_msg_to_client(c_socket, 1, 0, 'Must be logged in to perform this operation. Please login or create an account.')
                        continue
                    
                    with self.lock:
                        self.users.pop(c_name)
                        self.send_msg_to_client(c_socket, 0, 0, f'Account {c_name} has been deleted. You are now logged out.')

                    print(f'{c_name} has deleted their account.')
                    c_name = None
                    client = None

                # Exit the chat
                elif op == '6':
                    break
                
                # Request was malformed
                else:
                    self.send_msg_to_client(c_socket, 1, 0, 'Invalid operation. Please input your request as [operation]|[params].')
            
            if (client):
                print(f'\n[-] {c_name} has left. Disconnecting client.\n')
                client.disconnect()

        # Handle client disconnect if unexpected broken connection (e.g. ctrl+c)
        except (BrokenPipeError, ConnectionResetError) as e:
            if (client):
                print(f'\n[-] Connection with {c_name} has broken. Disconnecting client.\n')
                client.disconnect()

    # Main execution for starting server and listening for connections
    def start_server(self):
        try: 
            # Print out host/IP
            print(f'\n{self.host} ({self.ip})')

            # Bind socket to port
            self.s.bind((self.host, self.port))

            print('\nServer started!')

            # Listen for client connections
            self.s.listen(5)
            print('\nWaiting for incoming connections...')

            while True:
                c_socket, addr = self.s.accept()

                print(f'\n[+] Connected to {addr[0]} ({addr[1]})\n')

                # Start a new thread for each client
                t = threading.Thread(target=self.on_new_client, args=(c_socket, addr))
                t.start()

        except KeyboardInterrupt:
            print('\nServer closed with KeyboardInterrupt!')

            for c in self.users:
                if self.users[c].socket:
                    self.users[c].socket.close()

            self.s.close()

if __name__ == "__main__":
    server = Server()
    server.start_server()
