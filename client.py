import time, socket, sys
from threading import Thread

print('\nWelcome to Chat Room\n')
print('Initialising....\n')
time.sleep(1)

s = socket.socket()
host = socket.gethostname()
ip = socket.gethostbyname(host)
# host = 'dhcp-10-250-203-22.harvard.edu'
print(f'{host} ({ip})\n')

name = input('\nEnter your username: ')
port = 1538
print(f'\nTrying to connect to {host} ({port})\n')
time.sleep(1)
s.connect((host, port))
print('Connected...\n')

s.send(name.encode())


def receive_msgs():
    for msg in iter(lambda: s.recv(1024).decode(), ''):
        msg = msg.rsplit('<', 1) 
        sender = msg[1].strip()
        msg = msg[0].strip()

        print(f'{sender}: {msg}\n')

background_thread = Thread(target=receive_msgs)
background_thread.daemon = True
background_thread.start()

print(' -------------------------------------------------------------------------------------------------------------------')
print('|                                             Welcome to the Chat Room!                                             |')
print(' -------------------------------------------------------------------------------------------------------------------')

print('INSTRUCTIONS: To send a message to a user, please input your message followed by \'>\' and the recipient\'s username.\n')
print('For example:')
print('Hello there, Bob! > bobs_username_123\n')

print('Messages will appear with the sender\'s username in front. For example: ')
print('bob: Long time no see, Alice!\n')

print('ENTER [e] TO EXIT\n')

print(' -------------------------------------------------------------------------------------------------------------------')

while True:
    msg = input()
    s.send(msg.encode())

    if msg == '[e]':
        break