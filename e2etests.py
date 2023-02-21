import unittest, client, threading, time, sys, os
from random import randint

# TO RUN THESE TESTS, YOU MUST 1) run server.py, 2) change HOST to match the host of the server, and finally 3) run python e2etests.py

HOST = 'dhcp-10-250-203-22.harvard.edu'
    
class ChatAppTest(unittest.TestCase):
    def unpack_server_response(self, response):
        return {'status': ord(response[0]), 'is_chat': int(response[1]), 'msg': response[2:]}

    def assert_response_equal(self, response, status, is_chat, msg):
        self.assertEqual(status, response['status'])
        self.assertEqual(is_chat, response['is_chat'])
        self.assertEqual(msg, response['msg'])
        
    def assert_response_contains(self, response, status, is_chat, msg):
        self.assertEqual(status, response['status'])
        self.assertEqual(is_chat, response['is_chat'])
        self.assertIn(msg, response['msg'])

    # Test client-side input checks
    def test_validate_request(self):
        client1 = client.Client(host=HOST)

        with NoPrint():
            # Request too long
            self.assertEquals(client1.validate_request('list|' + 'a' * 280), 1)

            # Nonexistent op
            self.assertEquals(client1.validate_request('hello|there'), 1)

            # Blank username
            self.assertEquals(client1.validate_request('create'), 1)
            self.assertEquals(client1.validate_request('login| '), 1)

            # Malformed chat
            self.assertEquals(client1.validate_request('send'), 1)
            self.assertEquals(client1.validate_request('send|bob'), 1)
            self.assertEquals(client1.validate_request('send|bob|  '), 1)


        client1.sock.close()


    # Tests basic functionality of creating an account
    def test_create_account(self):
        client1 = client.Client(host=HOST)
        client1.sock.connect((client1.host, client1.port))

        # Create bob
        client1.pack_and_send_request('create|bob')

        response = self.unpack_server_response(client1.sock.recv(1024).decode())
        self.assert_response_equal(response, 0, 0, 'Account created! Logged in as bob.')

        # Attempt to create alice when logged in as bob
        client1.pack_and_send_request('create|alice')

        response = self.unpack_server_response(client1.sock.recv(1024).decode())
        self.assert_response_contains(response, 1, 0, 'Unable to create account: You are already logged in as bob.')

        # Another client attempts to create bob
        client2 = client.Client(host=HOST)
        client2.sock.connect((client1.host, client1.port))

        client2.pack_and_send_request('create|bob')

        response = self.unpack_server_response(client2.sock.recv(1024).decode())
        self.assert_response_equal(response, 1, 0, 'Unable to create account: This username is already taken.')

        # Delete for idempotency
        client1.pack_and_send_request('delete|bob')

        client1.sock.close()
        client2.sock.close()

    # Simulates race condition where 100 users are simultaneously creating account with same username
    def test_create_race(self):
        num_clients = 100
        clients = [None] * num_clients
        results = [None] * num_clients
        threads = [None] * num_clients

        def create_bob(c, i):
            time.sleep(randint(10, 100) * 10**-9 * (num_clients-i)**3)
            c.pack_and_send_request('create|bob')

            # Record if account creation was successful
            results[i] = 1 - self.unpack_server_response(c.sock.recv(1024).decode())['status']

        # Start 100 clients in diff threads
        for i in range(num_clients):
            clients[i] = client.Client(host=HOST)
            clients[i].sock.connect((clients[i].host, clients[i].port))
            
            threads[i] = threading.Thread(target=create_bob, args=(clients[i], i))
            threads[i].start()

        for i in range(num_clients):
            threads[i].join()

        # Only one client should have succeeded in creating the account
        self.assertEqual(1, sum(results))
        # print(results)

        # Delete for idempotency
        clients[results.index(1)].pack_and_send_request('delete|bob')

        for i in range(num_clients):
            clients[i].sock.close()

    # Test basic login functionality
    def test_login(self):
        # Create bob and alice
        client0 = client.Client(host=HOST)
        client0.sock.connect((client0.host, client0.port))
        client0.pack_and_send_request('create|alice')
        
        client1 = client.Client(host=HOST)
        client1.sock.connect((client1.host, client1.port))
        client1.pack_and_send_request('create|bob')
        client1.sock.close()

        # Login bob
        client1 = client.Client(host=HOST)
        client1.sock.connect((client1.host, client1.port))
        client1.pack_and_send_request('login|bob')

        response = self.unpack_server_response(client1.sock.recv(1024).decode())
        self.assert_response_equal(response, 0, 0, 'Logged in as bob.')
        client1.sock.recv(1024).decode()  # "No new messages while you've been gone"

        # Attempt to login alice on same client
        client1.pack_and_send_request('login|alice')

        response = self.unpack_server_response(client1.sock.recv(1024).decode())
        self.assert_response_contains(response,1, 0, 'Unable to login: You are already logged in as bob.')

        # Attempt login invalid user
        client2 = client.Client(host=HOST)
        client2.sock.connect((client2.host, client2.port))
        client2.pack_and_send_request('login|eve')

        response = self.unpack_server_response(client2.sock.recv(1024).decode())
        self.assert_response_contains(response,1, 0, 'Unable to login: This username does not exist.')

        # Attempt to log into bob even though he's active already
        client3 = client.Client(host=HOST)
        client3.sock.connect((client3.host, client3.port))
        client3.pack_and_send_request('login|bob')

        response = self.unpack_server_response(client3.sock.recv(1024).decode())
        self.assert_response_equal(response, 1, 0, 'Unable to login: This user is already connected to the server.')

        # Delete for idempotency
        client0.pack_and_send_request('delete|alice')
        client1.pack_and_send_request('delete|bob')

        client0.sock.close()
        client1.sock.close()
        client2.sock.close()
        client3.sock.close()

    # Simulates race condition where 100 users are simultaneously logging into the same account
    def test_login_race(self):
        client0 = client.Client(host=HOST)
        client0.sock.connect((client0.host, client0.port))
        client0.pack_and_send_request('create|bob')
        client0.sock.close()

        num_clients = 100
        clients = [None] * num_clients
        results = [None] * num_clients
        threads = [None] * num_clients

        def create_bob(c, i):
            time.sleep(randint(10, 100) * 10**-9 * (num_clients-i)**3)
            c.pack_and_send_request('login|bob')

            # Record if login was successful
            results[i] = 1 - self.unpack_server_response(c.sock.recv(1024).decode())['status']

        # Start 100 clients in diff threads
        for i in range(num_clients):
            clients[i] = client.Client(host=HOST)
            clients[i].sock.connect((clients[i].host, clients[i].port))
            
            threads[i] = threading.Thread(target=create_bob, args=(clients[i], i))
            threads[i].start()

        for i in range(num_clients):
            threads[i].join()

        # Only one client should have succeeded in logging into the account
        self.assertEqual(1, sum(results))

        # Delete for idempotency
        clients[results.index(1)].pack_and_send_request('delete|bob')

        for i in range(num_clients):
            clients[i].sock.close()

    # Test listing all account and wildcard filter
    def test_list_accounts(self):
        names = ['alice', 'bob', 'ashley', 'patrick']

        for name in names:
            c = client.Client(host=HOST)
            c.sock.connect((c.host, c.port))
            c.pack_and_send_request('create|' + name)
            c.sock.close()

        c = client.Client(host=HOST)
        c.sock.connect((c.host, c.port))

        # List all accounts
        c.pack_and_send_request('list')
        response = self.unpack_server_response(c.sock.recv(1024).decode())
        self.assert_response_equal(response, 0, 0, '\n- alice\n- bob\n- ashley\n- patrick\n')

        # List by wildcard
        c.pack_and_send_request('list|a*')
        response = self.unpack_server_response(c.sock.recv(1024).decode())
        self.assert_response_equal(response, 0, 0, '\n- alice\n- ashley\n')

        # Delete for idempotency
        for name in names:
            c.pack_and_send_request('login|' + name)
            time.sleep(0.01) # TODO: jank
            c.pack_and_send_request('delete|' + name)
            time.sleep(0.01)

        c.sock.close()

    # Test deleting accounts
    def test_delete_account(self):
        c = client.Client(host=HOST)
        c.sock.connect((c.host, c.port))

        # Attempt delete before login
        c.pack_and_send_request('delete|bob')

        response = self.unpack_server_response(c.sock.recv(1024).decode())
        self.assert_response_contains(response, 1, 0, 'Must be logged in to perform this operation.')

        # Create and delete
        c.pack_and_send_request('create|bob')
        c.sock.recv(1024).decode()

        c.pack_and_send_request('delete|bob')

        response = self.unpack_server_response(c.sock.recv(1024).decode())
        self.assert_response_equal(response, 0, 0, 'Account bob has been deleted. You are now logged out.')

        # Check account is actually deleted
        c.pack_and_send_request('login|bob')

        response = self.unpack_server_response(c.sock.recv(1024).decode())
        self.assert_response_contains(response, 1, 0, 'Unable to login: This username does not exist.')

        c.sock.close()

    def test_send_chat_invalid(self):
        # Attempt to send message before logged in
        client1 = client.Client(host=HOST)
        client1.sock.connect((client1.host, client1.port))
        client1.pack_and_send_request('send|alice|hi')
        response = self.unpack_server_response(client1.sock.recv(1024).decode())
        self.assert_response_contains(response, 1, 0, 'Must be logged in to perform this operation.')

        client1.pack_and_send_request('create|bob')
        client1.sock.recv(1024)

        # Attempt send message to invalid user
        client1.pack_and_send_request('send|ashley|hi')
        response = self.unpack_server_response(client1.sock.recv(1024).decode())
        self.assert_response_equal(response, 1, 0, 'Recipient username cannot be found.')

        # Attempt send message to oneself
        client1.pack_and_send_request('send|bob|hi')
        response = self.unpack_server_response(client1.sock.recv(1024).decode())
        self.assert_response_equal(response, 1, 0, 'Cannot send messages to yourself.')

        # Delete for idempotency
        client1.pack_and_send_request('delete|bob')
        client1.sock.close()

    def test_send_chat_live(self):
        # Create bob, alice, and eve
        client1 = client.Client(host=HOST)
        client1.sock.connect((client1.host, client1.port))
        client1.pack_and_send_request('create|bob')
        client1.sock.recv(1024)

        client2 = client.Client(host=HOST)
        client2.sock.connect((client2.host, client2.port))
        client2.pack_and_send_request('create|alice')
        client2.sock.recv(1024)

        client3 = client.Client(host=HOST)
        client3.sock.connect((client3.host, client3.port))
        client3.pack_and_send_request('create|eve')
        client3.sock.recv(1024)

        # Send messages to bob live
        client2.pack_and_send_request('send|bob|hi')
        response = self.unpack_server_response(client1.sock.recv(1024).decode())
        self.assert_response_equal(response, 0, 1, 'alice|hi')

        client3.pack_and_send_request('send|bob|hey')
        response = self.unpack_server_response(client1.sock.recv(1024).decode())
        self.assert_response_equal(response, 0, 1, 'eve|hey')

        # Delete for idempotency
        client1.pack_and_send_request('delete|bob')
        client2.pack_and_send_request('delete|alice')
        client3.pack_and_send_request('delete|eve')

        client1.sock.close()
        client2.sock.close()
        client3.sock.close()

    def test_send_chat_queue(self):
         # Create bob, alice, and eve
        client1 = client.Client(host=HOST)
        client1.sock.connect((client1.host, client1.port))
        client1.pack_and_send_request('create|bob')
        client1.sock.recv(1024)
        client1.sock.close()

        client2 = client.Client(host=HOST)
        client2.sock.connect((client2.host, client2.port))
        client2.pack_and_send_request('create|alice')
        client2.sock.recv(1024)

        client3 = client.Client(host=HOST)
        client3.sock.connect((client3.host, client3.port))
        client3.pack_and_send_request('create|eve')
        client3.sock.recv(1024)
        
        # Queue messages to bob
        client2.pack_and_send_request('send|bob|hello there')
        time.sleep(0.01) # so that order is deterministic
        client3.pack_and_send_request('send|bob|what is up')

        client1 = client.Client(host=HOST)
        client1.sock.connect((client1.host, client1.port))
        client1.pack_and_send_request('login|bob')
        client1.sock.recv(1024)

        response = self.unpack_server_response(client1.sock.recv(1024).decode())
        self.assert_response_equal(response, 0, 1, 'alice|hello there')

        response = self.unpack_server_response(client1.sock.recv(1024).decode())
        self.assert_response_equal(response, 0, 1, 'eve|what is up')

        # Delete for idempotency
        client1.pack_and_send_request('delete|bob')
        client2.pack_and_send_request('delete|alice')
        client3.pack_and_send_request('delete|eve')

        client1.sock.close()
        client2.sock.close()
        client3.sock.close()


class NoPrint(object):
    def __init__(self,stdout = None, stderr = None):
        self.devnull = open(os.devnull,'w')
        self._stdout = stdout or self.devnull or sys.stdout
        self._stderr = stderr or self.devnull or sys.stderr

    def __enter__(self):
        self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
        self.old_stdout.flush(); self.old_stderr.flush()
        sys.stdout, sys.stderr = self._stdout, self._stderr

    def __exit__(self, exc_type, exc_value, traceback):
        self._stdout.flush(); self._stderr.flush()
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
        self.devnull.close()


if __name__ == '__main__':
    unittest.main()