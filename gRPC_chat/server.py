from concurrent import futures
from collections import deque
import grpc
import chat_pb2
import chat_pb2_grpc
import socket
import fnmatch
import threading
from time import sleep

'''
A ClientModel object represents an account that is created. It keeps track of the username, whether the user 
is active or not, and the messages to be delivered to the user.
'''
class ClientModel:
    def __init__(self, name, active=False):
        self.name = name
        self.msgs = deque([])
        self.active = active
        self.lock = threading.Lock()
        self.msg_number = 0

    def disconnect(self):
        self.active = False


'''
The ChatServer class contains the set of all clients/users that have connected to the server. It also contains
stub functions the client can use to communicate with the server.
'''
class ChatServer(chat_pb2_grpc.GreeterServicer):
    def __init__(self):
        self.clients = {}
        self.lock = threading.Lock()

    # A stream of messages that the client listens to and receives
    def ChatStream(self, request, context):
        while True:
            # only send messages to active users
            if self.clients[request.name].active:
                msgs = self.clients[request.name].msgs
                while msgs:
                    msg = msgs.popleft()
                    yield msg
                sleep(0.1)

    # Used by the client to send messages to other clients. The server acts as an intermediary
    # to add messages to a client's queue.
    def SendNote(self, request, context):
        status = 0
        sender = 1
        receiver = request.recipient
        msg = ''
        if receiver not in self.clients:
            msg = 'ERROR: Recipient username cannot be found.\n'
            status = 1
            sender = 0
        else:
            self.clients[receiver].msgs.append(request)
        return chat_pb2.Response(message=msg, status=status, sender=sender)

    # Method for listing accounts. Message input accounts for wildcards.
    def ListAccounts(self, request, context):
        status = 0
        sender = 0
        accounts = '\n'
        msg = request.message
        if self.clients:
            for key in fnmatch.filter(self.clients.keys(), msg if msg else '*'):
                accounts += '- ' + key + '\n'
        else:
            accounts = "No accounts have been created."
        return chat_pb2.Response(message=accounts, status=status, sender=sender)

    # Method for deleting accounts.
    def DeleteAccount(self, request, context):
        status = 0
        sender = 0
        with self.lock:
            self.clients.pop(request.name)
            return chat_pb2.Response(message=f'Account {request.name} has been deleted. You are now logged out.',
                                     status=status, sender=sender)

    # Method for creating an account. Returns an error if user already exists
    def CreateAccount(self, request, context):
        status = 0
        sender = 0
        with self.lock:
            name = request.name
            # Username is already registered
            if name in self.clients:
                response = 'Unable to create account: This username is already taken.'
                status = 1

            # Register user - create new client model
            else:
                self.clients[name] = ClientModel(name, True)
                response = f'Account created! Logged in as {name}.'
                print(f'{name} has created an account.')

            return chat_pb2.Response(message=response, status=status, sender=sender)

    # Method for login. Returns an error if user is already active or if username doesn't exist.
    def Login(self, request, context):
        status = 0
        sender = 0

        with self.lock:
            name = request.name
            if name not in self.clients:
                response = 'Unable to login: This username does not exist. If you would like to use this username, please create a new account.'
                status = 1
            elif self.clients[name].active:
                response = 'Unable to login: This user is already connected to the server.'
                status = 1
            else:
                self.clients[name].active = True
                response = f'Logged in as {request.name}.'
                print(f'{name} is logged in.')

        return chat_pb2.Response(message=response, status=status, sender=sender)

    # Sets active status to False and appends a disconnected message to queue
    def Disconnect(self, request, context):
        self.clients[request.name].active = False
        self.clients[request.name].msgs.append(chat_pb2.Note(message=''))
        return chat_pb2.String(message='')


def main():
    try:
        host = socket.gethostname()
        ip = socket.gethostbyname(host)
        port = '1539'
        print(f'\n{host} ({ip})')

        # start server
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        chat_pb2_grpc.add_GreeterServicer_to_server(ChatServer(), server)
        print('\nServer started!')
        print('\nWaiting for incoming connections...')

        # connect server to host:port
        server.add_insecure_port(f'{host}: {port}')
        server.start()
        server.wait_for_termination()

    except KeyboardInterrupt:
        # TODO: close all client sockets too
        print('\nServer closed with KeyboardInterrupt!')
        server.stop(grace=0.1)


if __name__ == "__main__":
    main()
