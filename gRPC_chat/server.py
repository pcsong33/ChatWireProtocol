from concurrent import futures
from collections import deque
import grpc
import chat_pb2
import chat_pb2_grpc
import socket



class Client:
    def __init__(self, name):
        self.name = name
        self.msgs = deque([])
        self.active = False


clients = {}


class ChatServer(chat_pb2_grpc.GreeterServicer):

    def ChatStream(self, request, context):
        msgs = clients[request.name].msgs
        while True:
            while msgs:
                msg = msgs.popleft()
                yield msg

    def SendNote(self, request, context):

        msg = request.message.rsplit('>', 1)

        # Handle Invalid Inputs
        if len(msg) < 2:
            print('ERROR: No recipient specified. To send a message to a user, please input your message followed by \'>\' and the recipient\'s username.\n')

        receiver = msg[1].strip()
        msg = msg[0].strip()

        if receiver not in clients:
            print('ERROR: Recipient username cannot be found.\n'.encode())

        if receiver == request.sender:
            print('ERROR: Cannot send messages to yourself.\n'.encode())

        if msg == '':
            print('ERROR: Cannot send blank message.\n'.encode())

        note = chat_pb2.Note()
        note.message = msg
        note.sender = request.sender
        clients[receiver].msgs.append(note)

        return chat_pb2.Empty()

    def ValidateUser(self, request, context):
        c_name = request.name
        if c_name in clients:
            # user is not already logged in - connect to server
            if not clients[c_name].active:
                clients[c_name].active = True
                return chat_pb2.UserValidation(message=True)
            # user is already logged in - refuse connection
            else:
                return chat_pb2.UserValidation(message=False)

        else:
            clients[c_name] = Client(c_name)
            return chat_pb2.UserValidation(message=True)


def main():
    try:
        host = socket.gethostname()
        ip = socket.gethostbyname(host)
        port = '1538'
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
