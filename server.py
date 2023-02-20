import time, socket
import fnmatch
import threading

PORT = 1538

class Client:
    def __init__(self, name, socket=None, addr=None):
        self.name = name
        self.socket = socket
        self.addr = addr
        self.active = True
        self.msgs = []
        self.lock = threading.Lock()
    
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
        # Multiple clients on diff threads may attempt to queue msgs simultaneously
        with self.lock:
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

            # Create an account
            if op == '1':
                # Client is already logged in
                if client:
                    send_message(c_socket, 1, 0, f'Unable to create account: You are already logged in as {c_name}. Please exit and start a new client to log into a different account.')
                    continue
                # Username is already registered
                if msg in clients:
                    send_message(c_socket, 1, 0, 'Unable to create account: This username is already taken.')
                    continue

                c_name = msg
                clients[c_name] = Client(c_name, c_socket, addr)
                client = clients[c_name]
                send_message(c_socket, 0, 0, f'Account created! Logged in as {c_name}.')
        
            # Log into existing account
            elif op == '2':
                # Client is already logged in
                if client:
                    send_message(c_socket, 1, 0, f'Unable to login: You are already logged in as {c_name}. Please exit  and start a new client to log into a different account.')
                    continue
                # Username does not exist
                if msg not in clients:
                    send_message(c_socket, 1, 0, 'Unable to login: This username does not exist. If you would like to use this username, please create a new account.')
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
                time.sleep(0.0001)

                # Send any undelivered messages 
                if (len(client.msgs) > 0):
                    for sender, queued_msg in client.msgs:
                        send_message(c_socket, 0, 1, sender + '|' + queued_msg)
                        print(f'{sender} sent {queued_msg} to {c_name}')
                        time.sleep(0.0001) # TODO: this is jank

                    send_message(c_socket, 2, 0, 'Messages you missed while you were away have been delivered above.')
                    client.clear_msgs()
                else:
                     send_message(c_socket, 2, 0, 'No new messages since you\'ve been gone.')

            # Send message to another client
            elif op == '3':
                # Must be logged in
                if not client:
                    send_message(c_socket, 1, 0, 'Must be logged in to perform this operation. Please login or create an account.')
                    continue
                
                msg = msg.split('|', 1)

                receiver = msg[0].strip()
                msg = msg[1].strip()

                # Validate recipient
                if receiver not in clients:
                    send_message(c_socket, 1, 0, 'Recipient username cannot be found.')
                    continue
                if receiver == c_name:
                    send_message(c_socket, 1, 0, 'Cannot send messages to yourself.')
                    continue
                
                # Send/Queue Message
                receiver_client = clients[receiver]

                if not receiver_client.socket:
                    receiver_client.queue_msg(c_name, msg)
                    send_message(c_socket, 0, 0, f'Message sent to {receiver}.')
                    print(f'{c_name} queued {msg} to {receiver}')
                else:
                    try:
                        send_message(receiver_client.socket, 0, 1, c_name + '|' + msg)
                        send_message(c_socket, 0, 0, f'Message sent to {receiver}.')
                        print(f'{c_name} sent {msg} to {receiver}')
                    except BrokenPipeError:
                        send_message(c_socket, 1, 0, f'Message could not be sent to {receiver}. Please try again.')
                        print(f'\n[-] Connection with {receiver_client.name} has broken. Disconnecting client.\n')
                        receiver_client.disconnect()

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
                    send_message(c_socket, 1, 0, 'Must be logged in to perform this operation. Please login or create an account.')
                    continue

                clients.pop(c_name) # TODO: maybe need stuff with locks here?
                c_name = None
                client = None

            # Exit the chat
            elif op == '6':
                break
            
            # Request was malformed
            else:
                send_message(c_socket, 1, 0, 'Invalid operation. Please input your request as [operation]|[params].')
        
        if (client):
            print(f'\n[-] {c_name} has left. Disconnecting client.\n')
            client.disconnect()

    except (BrokenPipeError, ConnectionResetError) as e:
        if (client):
            print(f'\n[-] Connection with {c_name} has broken. Disconnecting client.\n')
            client.disconnect()

def main():
    try:
        s = socket.socket()
        host = socket.gethostname()
        ip = socket.gethostbyname(host)

        print(f'\n{host} ({ip})')

        s.bind((host, PORT))
        print('\nServer started!')

        s.listen(5)
        print('\nWaiting for incoming connections...')

        while True:
            c_socket, addr = s.accept()

            print(f'\n[+] Connected to {addr[0]} ({addr[1]})\n')

            t = threading.Thread(target=on_new_client, args=(c_socket, addr))
            t.start()

    except KeyboardInterrupt:
        print('\nServer closed with KeyboardInterrupt!')

        for c in clients:
            if clients[c].socket:
                clients[c].socket.close()

        s.close()


if __name__ == "__main__":
    main()
