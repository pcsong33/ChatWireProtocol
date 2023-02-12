import time, socket, sys
from threading import Thread
from collections import deque

clients = {}

def on_new_client(c_socket, addr, c_name):
    print(f'\n[+] Connected to {c_name} at {addr[0]} ({addr[1]})\n')

    while True:
        msg = c_socket.recv(1024).decode()

        if msg == '[e]':
            break

        msg = msg.rsplit('>', 1)
        
        if len(msg) < 2:
            c_socket.send('No recipient specified. To send a message to a user, please input your message followed by \'>\' and the recipient\'s username. < ERROR'.encode())
            continue

        receiver = msg[1].strip()
        msg = msg[0].strip()
        
        if receiver not in clients:
            c_socket.send('Recipient username cannot be found. < ERROR'.encode())
            continue
        if receiver == c_name:
            c_socket.send('Cannot send messages to yourself. < ERROR'.encode())
            continue
        if msg == '':
            c_socket.send('Cannot send blank message < ERROR'.encode())
            continue

        clients[receiver][0].send((msg + '<' + c_name).encode())

        print(f'{c_name} sent {msg} to {receiver}')

    print(f'\n[-] {c_name} has left. Disconnecting client.\n')
    c_socket.close()

try:
    s = socket.socket()
    host = socket.gethostname()
    # host = "dhcp-10-250-203-22.harvard.edu"
    ip = socket.gethostbyname(host)
    port = 1538
    print(f'\n{host} ({ip})')

    s.bind((host, port))
    print('\nServer started!')

    s.listen(5)
    print('\nWaiting for incoming connections...')

    while True:
        c_socket, addr = s.accept()
        c_name = c_socket.recv(1024).decode().strip()
        clients[c_name] = [c_socket, []] # TODO: check if user already exists

        t = Thread(target=on_new_client, args=(c_socket, addr, c_name))
        t.start()

except KeyboardInterrupt:
    # TODO: close all client sockets too
    print('\nServer closed with KeyboardInterrupt!')
    s.close()