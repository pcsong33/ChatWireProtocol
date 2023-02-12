import time, socket, sys
from threading import Thread
from collections import deque

clients = {}

def on_new_client(c_socket, addr):
    c_name = c_socket.recv(1024).decode()
    clients[c_name] = [True, []]

    print(f'\n[+] Connected to {c_name} at {addr[0]} ({addr[1]})\n')

    while True:
        # receiver = c_socket.recv(1024).decode()
        msg = c_socket.recv(1024).decode()

        if msg == '[e]':
            break

        print(f'{c_name} sent {msg}')

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
        t = Thread(target=on_new_client, args=(c_socket, addr))
        t.start()
        
except KeyboardInterrupt:
    print('\nServer closed with KeyboardInterrupt!')
    s.close()