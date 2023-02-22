from concurrent import futures
from collections import deque
import grpc
import chat_pb2
import chat_pb2_grpc
import socket
import fnmatch
import threading
from time import sleep


class ClientModel:
    def __init__(self, name, active=False):
        self.name = name
        self.msgs = deque([])
        self.active = active
        self.lock = threading.Lock()

    def disconnect(self):
        self.active = False


clients = {}


class ChatServer(chat_pb2_grpc.GreeterServicer):
    def __init__(self):
        self.clients = {}
        self.lock = threading.Lock()

    def ChatStream(self, request, context):
        while True:
            msgs = self.clients[request.name].msgs
            while msgs:
                msg = msgs.popleft()
                yield msg
            sleep(0.1)

    def SendNote(self, request, context):

        receiver = request.recipient

        if receiver not in self.clients:
            msg = 'ERROR: Recipient username cannot be found.\n'
            request.message = msg
        else:
            self.clients[receiver].msgs.append(request)
        return chat_pb2.Empty()

    def ValidateUser(self, request, context):
        c_name = request.name
        if c_name in self.clients:
            # user is not already logged in - connect to server
            if not self.clients[c_name].active:
                self.clients[c_name].active = True
                return chat_pb2.UserValidation(message=True)
            # user is already logged in - refuse connection
            else:
                return chat_pb2.UserValidation(message=False)

        else:
            self.clients[c_name] = ClientModel(c_name)
            self.clients[c_name].active = True

        return chat_pb2.UserValidation(message=True)

    def ListAccounts(self, request, context):
        accounts = '\n'
        msg = request.message
        if self.clients:
            for key in fnmatch.filter(self.clients.keys(), msg if msg else '*'):
                accounts += '- ' + key + '\n'
        else:
            accounts = "No accounts have been created."
        return chat_pb2.String(message=accounts)

    def DeleteAccount(self, request, context):
        with self.lock:
            self.clients.pop(request.name)
            return chat_pb2.String(message=f'Account {request.name} has been deleted. You are now logged out.')

    def CreateAccount(self, request, context):
        with self.lock:
            name = request.name
            # Username is already registered
            if name in self.clients:
                response = 'Unable to create account: This username is already taken.'

            # Register user - create new client model
            else:
                self.clients[name] = ClientModel(name, True)
                response = f'Account created! Logged in as {name}'
                print(f'{name} has created an account.')

            return chat_pb2.String(message=response)

    def Login(self, request, context):
        name = request.name
        response = ''
        with self.clients[name].lock:
            if name not in self.clients:
                response = 'Unable to login: This username does not exist. If you would like to use this username, please create a new account.'
            elif self.clients[name].active:
                response = 'Unable to login: This user is already connected to the server.'
            else:
                self.clients[name].active = True
                response = f'Logged in as{request.name}'
                print(f'{name} is logged in.')

        return chat_pb2.String(message=response)

    def Disconnect(self, request, context):
        self.clients[request.name].active = False
        return chat_pb2.String(message='')


def main():
    try:
        host = socket.gethostname()
        ip = socket.gethostbyname(host)
        port = '1539'
        print(f'\n{host} ({ip})')

        print('\nServer started!')
        print('\nWaiting for incoming connections...')

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        chat_pb2_grpc.add_GreeterServicer_to_server(ChatServer(), server)

        server.add_insecure_port(f'{host}: {port}')
        server.start()
        server.wait_for_termination()

    except KeyboardInterrupt:
        # TODO: close all client sockets too
        print('\nServer closed with KeyboardInterrupt!')
        server.stop()


if __name__ == "__main__":
    main()
