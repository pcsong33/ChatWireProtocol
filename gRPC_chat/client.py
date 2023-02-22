import grpc
import chat_pb2
import chat_pb2_grpc
import time
import socket
from threading import Thread

MAX_REQUEST_LEN = 280

# Change this below to match the server host
HOST = 'dhcp-10-250-203-22.harvard.edu'

# Set of valid operations
OPS = set(['create', 'login', 'send', 'list', 'delete', 'exit'])

'''
The Client object connects to the server running the chat application. It listens for incoming messages from 
the server. It also takes in requests from the user via command-line input and calls stub functions to communicate
with the server.
'''
class Client:
    def __init__(self):
        self.conn = None
        self.name = None
        self.channel = None
        self.thread = None

    def print_intro_message(self):
        print(
            ' -------------------------------------------------------------------------------------------------------------------')
        print(
            '|                                             Welcome to the Chat Room!                                             |')
        print(
            ' -------------------------------------------------------------------------------------------------------------------')

        print('INSTRUCTIONS: This chat room supports the following requests in the format \'[request type]|[params]\'')
        print('- create|[username] --> Create account')
        print('- login|[username] --> Log into existing account')
        print('- send|[recipient]|[message] --> Send a message to another user')
        print(
            '- list|[wildcard (optional)] --> List accounts, via Unix shell-style wildcard (no wildcard = all accounts listed)')
        print('- delete --> Delete account')
        print('- exit --> Exit the chat application')

        print(
            ' --------------------------------------------------------------------------------------------------------------------')

    # Method to receive client-to-client messages.
    def receive_msgs(self):
        try:
            msgs = self.conn.ChatStream(chat_pb2.UserName(name=self.name))
            if msgs:
                for note in msgs:
                    # print error message
                    if note.sender == "ERROR":
                        print(note.message)
                    else:
                        print(f'\nMessage from {note.sender}: {note.message}\n')
        except Exception:
            print('Channel closed!')

    # Parses through user input and validates a request. Once request had been verified,
    # calls a stub function and connects to the server
    def validate_and_send_request(self, request):
        # Length limit
        if len(request) > MAX_REQUEST_LEN:
            print('\nINPUT ERROR: Please limit requests to 280 characters.\n')
            return 1

        op, msg = request.split('|', 1) if '|' in request else (request, '')
        op, msg = op.strip(), msg.strip()

        # Operation does not exist
        if op not in OPS:
            print('\nINPUT ERROR: Invalid operation. Please input your request as [operation]|[params].\n')
            return 1

        # Validate and handle request types
        if op == 'create' or op == 'login':
            res = ''

            # Account validation
            if not msg:
                print('\nINPUT ERROR: Unable to create account: Username cannot be blank.\n')
                return 1

            if op == 'create':
                if self.name:
                    print(f'\nUnable to create account: You are already logged in as {self.name}\n')
                    return 1
                res = self.conn.CreateAccount(chat_pb2.UserName(name=msg))

            if op == 'login':
                if self.name:
                    print(f'\nYou are already logged in as {self.name}. Please exit and start a new client to log into a different account.\n')
                    return 1
                res = self.conn.Login(chat_pb2.UserName(name=msg))

            if res.status == 1:
                print(res.message)
                return 1

            # Login successful
            self.name = msg

            # Start background thread for receiving chat messages once logged in
            self.thread = Thread(target=self.receive_msgs)
            self.thread.daemon = True
            self.thread.start()
            print(res.message)

        elif op == 'list':
            accounts = self.conn.ListAccounts(chat_pb2.String(message=msg))
            print(accounts.message)

        elif op == 'delete':
            if self.name:
                accounts = self.conn.DeleteAccount(chat_pb2.UserName(name=self.name))
                self.name = None
                print(accounts.message)
            else:
                print('\nMust be logged in to perform this operation. Please login or create an account.\n')
                return 1

        elif op == 'exit':
            return 2

        elif op == 'send':
            msg_params = msg.split('|', 1)

            # Parameter validation
            if not self.name:
                print("\nERROR: You must be logged in to send a message\n")
                return 1
            if len(msg_params) < 2:
                print('\nINPUT ERROR: Not enough parameters specified. To send a message to another user, please type send|[recipient]|[message].\n')
                return 1
            if msg_params[1].strip() == '':
                print('\nINPUT ERROR: Message cannot be blank.\n')
                return 1
            if msg_params[0] == self.name:
                print('\nERROR: Cannot send messages to yourself.\n')
                return 1

            note = chat_pb2.Note(
                sender=self.name,
                recipient=msg_params[0],
                message=msg_params[1]
            )
            response = self.conn.SendNote(note)
            print(response.message)

    def connect_to_server(self):
        print('\nWelcome to Chat Room\n')
        print('Initialising....\n')
        time.sleep(1)
        port = 1539
        print(f'\nTrying to connect to {HOST} ({port})\n')

        with grpc.insecure_channel(f'{HOST}:{port}') as channel:
            # Connect to server via gRPC
            connection = chat_pb2_grpc.GreeterStub(channel)
            self.conn = connection
            self.channel = channel
            print('Connected...\n')
            self.print_intro_message()

            # Send message to the server to deliver to recipient
            try:
                while True:
                    request = input()

                    status = self.validate_and_send_request(request)

                    # Continue if request is invalid
                    if status == 1:
                        continue

                    # Client is exiting
                    if status == 2:
                        if self.name:
                            self.conn.Disconnect(chat_pb2.UserName(name=self.name))
                        return
            
            # Gracefully handle keyboard interrupt
            except KeyboardInterrupt:
                if self.name:
                    self.conn.Disconnect(chat_pb2.UserName(name=self.name))



if __name__ == "__main__":
    client = Client()
    client.connect_to_server()


