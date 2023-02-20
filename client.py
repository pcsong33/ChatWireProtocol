import time, socket, sys
from threading import Thread

MAX_REQUEST_LEN = 280

OP_TO_OPCODE = {
    'create': '1',
    'login': '2',
    'send': '3',
    'list': '4',
    'delete': '5',
    'exit': '6'
}

# Background thread listens for incoming messages to print
def receive_msgs(s):
    # Messages send as [status][is_chat][msg]
    for msg in iter(lambda: s.recv(1024).decode(), ''):
        status, is_chat, msg = ord(msg[0]), int(msg[1]), msg[2:]

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

# TODO: fix intro message

# def print_intro_message():
#     print(' -------------------------------------------------------------------------------------------------------------------')
#     print('|                                             Welcome to the Chat Room!                                             |')
#     print(' -------------------------------------------------------------------------------------------------------------------')

#     print('INSTRUCTIONS: To send a message to a user, please input your message followed by \'>\' and the recipient\'s username.\n')
#     print('For example:')
#     print('Hello there, Bob! > bobs_username_123\n')

#     print('Messages will appear with the sender\'s username in front. For example: ')
#     print('bob: Long time no see, Alice!\n')

#     print('Enter LIST to list all accounts')
#     print('Enter DELETE to delete your account')

#     print('ENTER [e] TO EXIT\n')

#     print(' -------------------------------------------------------------------------------------------------------------------')


def main():
    print('\nWelcome to Chat Room\n')
    print('Initialising....\n')
    time.sleep(1)

    s = socket.socket()
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    # host = 'dhcp-10-250-203-22.harvard.edu'
    print(f'{host} ({ip})\n')

    port = 1538
    print(f'\nTrying to connect to {host} ({port})\n')
    time.sleep(1)
    s.connect((host, port))
    print('Connected...\n')

    background_thread = Thread(target=receive_msgs, args=(s,))
    background_thread.daemon = True
    background_thread.start()

    # print_intro_message()

    # Send message to the server to deliver to recipient
    while True:
        request = input()

        # Limit request length
        if len(request) > MAX_REQUEST_LEN:
            print('\nINPUT ERROR: Please limit requests to 280 characters.\n')
            continue

        op, msg = request.split('|', 1) if '|' in request else (request, '')
        op, msg = op.strip(), msg.strip()

        # Operation does not exist
        if op not in OP_TO_OPCODE:
            print('\nINPUT ERROR: Invalid operation. Please input your request as [operation]|[params].\n')
            continue

        opcode = OP_TO_OPCODE[op]
        encoded_request = (opcode + '|' + msg).encode() # TODO: send with header?
        s.send(encoded_request) 

        # Client is exiting 
        if op == 'exit':
            break


if __name__ == "__main__":
    main()
