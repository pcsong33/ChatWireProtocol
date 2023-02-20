import grpc
import chat_pb2
import chat_pb2_grpc
import time
import socket
from threading import Thread


def print_intro_message():
    print(' -------------------------------------------------------------------------------------------------------------------')
    print('|                                             Welcome to the Chat Room!                                             |')
    print(' -------------------------------------------------------------------------------------------------------------------')

    print('INSTRUCTIONS: To send a message to a user, please input your message followed by \'>\' and the recipient\'s username.\n')
    print('For example:')
    print('Hello there, Bob! > bobs_username_123\n')

    print('Messages will appear with the sender\'s username in front. For example: ')
    print('bob: Long time no see, Alice!\n')

    print('Enter LIST to list all accounts')
    print('Enter DELETE to delete your account')

    print('ENTER [e] TO EXIT\n')

    print('-------------------------------------------------------------------------------------------------------------------')


def receive_msgs(stub, name):
    msgs = stub.ChatStream(chat_pb2.UserName(name=name))
    if msgs:
        for note in msgs:
            print(f'{note.sender}: {note.message}')


def main():
    print('\nWelcome to Chat Room\n')
    print('Initialising....\n')
    time.sleep(1)
    host = socket.gethostname()
    ip = socket.gethostbyname(host)

    print(f'{host} ({ip})\n')

    name = input('\nEnter your username: ')
    port = 1538

    try:
        with grpc.insecure_channel(f'{host}:{port}') as channel:
            connection = chat_pb2_grpc.GreeterStub(channel)
            validation = connection.ValidateUser(chat_pb2.UserName(name=name))

            if validation:
                print("Connected!")
            else:
                print("You are already connected!")
                channel.close()
                return

            print_intro_message()

            background_thread = Thread(target=receive_msgs, args=(connection, name))
            background_thread.daemon = True
            background_thread.start()

            while True:
                msg = input()

                if msg == '[e]':
                    channel.close()
                    break

                if msg == 'DELETE':
                    channel.close()
                    break

                note = chat_pb2.Note()
                note.message = msg
                note.sender = name
                connection.SendNote(note)

    except grpc.RpcError as rpc_error:
        print("Done")




if __name__ == "__main__":
    main()


