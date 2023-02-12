import time, socket, sys

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

while True:
    # receiver = input('Send chat to: ')
    msg = input('Message (Enter [e] to exit): ')
    # s.send(receiver.encode())
    s.send(msg.encode())

    if msg == '[e]':
        break