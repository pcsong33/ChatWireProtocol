import time, socket
from threading import Thread

MAX_REQUEST_LEN = 280

NUM_HEADER_BYTES = 3

OP_TO_OPCODE = {
    'create': '1',
    'login': '2',
    'send': '3',
    'list': '4',
    'delete': '5',
    'exit': '6'
}

class Client:
    def __init__(self, host='dhcp-10-250-203-22.harvard.edu', port=1538):
        self.sock = socket.socket()
        self.host = host
        self.port = port

    def print_intro_message(self):
        print(' -------------------------------------------------------------------------------------------------------------------')
        print('|                                             Welcome to the Chat Room!                                             |')
        print(' -------------------------------------------------------------------------------------------------------------------')

        print('INSTRUCTIONS: This chat room supports the following requests in the format \'[request type]|[params]\'')
        print('- create|[username] --> Create account')
        print('- login|[username] --> Log into existing account')
        print('- send|[recipient]|[message] --> Send a message to another user')
        print('- list|[wildcard (optional)] --> List accounts, via Unix shell-style wildcard (no wildcard = all accounts listed)')
        print('- delete --> Delete account')
        print('- exit --> Exit the chat application')

        print(' --------------------------------------------------------------------------------------------------------------------')
    
    # Receive exactly k bytes from the server
    def recv_k_bytes(self, k):
        bytes_recd = 0
        msg = ''

        while bytes_recd < k:
            next_recv = self.sock.recv(k - bytes_recd).decode()

            if next_recv == b'':
                raise RuntimeError("Server connection broken.")

            bytes_recd += len(next_recv)
            msg += next_recv
            
        return msg

    # Receive a single response from the server
    def recv_response_from_server(self):
        # Messages send as [msg_len][status][is_chat][msg]
        header = self.recv_k_bytes(NUM_HEADER_BYTES)
        msg_len, status, is_chat = ord(header[0]), ord(header[1]), int(header[2])
        msg = self.recv_k_bytes(msg_len)

        return status, is_chat, msg

    # For background thread that listens for incoming messages to print
    def print_messages_from_server(self):
        status, is_chat, msg = self.recv_response_from_server()

        while msg:
            # Message from another client
            if is_chat:
                msg = msg.split('|', 1)
                sender = msg[0].strip()
                msg = msg[1].strip()

                print(f'\nMessage from {sender}: {msg}\n')
            # Message from the server
            else:
                if status == 0:
                    print(f'\nSUCCESS: {msg}\n')
                elif status == 1:
                    print(f'\nERROR: {msg}\n')
                elif status == 2:
                    print(f'\nSERVER MESSAGE: {msg}\n')
            
            status, is_chat, msg = self.recv_response_from_server()


    # Validate requests before sending to server
    def validate_request(self, request):
        # Length limit
        if len(request) > MAX_REQUEST_LEN:
            print('\nINPUT ERROR: Please limit requests to 280 characters.\n')
            return 1

        op, msg = request.split('|', 1) if '|' in request else (request, '')
        op, msg = op.strip(), msg.strip()

        # Operation does not exist
        if op not in OP_TO_OPCODE:
            print('\nINPUT ERROR: Invalid operation. Please input your request as [operation]|[params].\n')
            return 1

        # Validate parameters
        if op == 'create' or op == 'login':
            if not msg:
                print('\nINPUT ERROR: Unable to create account: Username cannot be blank.\n')
                return 1
        elif op == 'send':
            msg_params = msg.split('|', 1)
            if len(msg_params) < 2:
                print('\nINPUT ERROR: Not enough parameters specified. To send a message to another user, please type 3|[recipient]|[message].\n')
                return 1
            if msg_params[1].strip() == '':
                print('\nINPUT ERROR: Message cannot be blank.\n')
                return 1

        return 0

    # Encode request to match wire protocol and send to server
    def pack_and_send_request(self, request):
        op, msg = request.split('|', 1) if '|' in request else (request, '')
        op, msg = op.strip(), msg.strip()

        opcode = OP_TO_OPCODE[op]
        encoded_request = (opcode + '|' + msg).encode() # TODO: send with header?
        self.sock.send(encoded_request) 

    # Main execution for communicating with chat server
    def connect_to_server(self):
        print('\nWelcome to Chat Room\n')
        print('Initialising....\n')
        time.sleep(1)

        print(f'\nTrying to connect to {self.host} ({self.port})\n')
        time.sleep(1)
        self.sock.connect((self.host, self.port))
        print('Connected...\n')

        background_thread = Thread(target=self.print_messages_from_server)
        background_thread.daemon = True
        background_thread.start()

        self.print_intro_message()

        # Send message to the server to deliver to recipient
        while True:
            request = input()

            status = self.validate_request(request)

            # Continue if request is invalid
            if status == 1:
                continue

            # Send request to server
            self.pack_and_send_request(request)

            # Client is exiting 
            if request.split('|', 1)[0] == 'exit':
                break
            

if __name__ == "__main__":
    client = Client()
    client.connect_to_server()
