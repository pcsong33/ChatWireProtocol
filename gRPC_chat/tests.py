import unittest, client, threading, time, sys, os, grpc, socket, chat_pb2_grpc, chat_pb2
from random import randint

# TO RUN THESE TESTS, YOU MUST 1) run server.py, 2) change HOST to match the host of the server, and finally 3) run python tests.py

HOST = socket.gethostname()
PORT = 1539


class ChatAppTest(unittest.TestCase):
    def assert_response_equal(self, response, status, is_chat, msg):
        self.assertEqual(status, response.status)
        self.assertEqual(is_chat, response.sender)
        self.assertEqual(msg, response.message)

    def assert_response_contains(self, response, status, is_chat, msg):
        self.assertEqual(status, response.status)
        self.assertEqual(is_chat, response.sender)
        self.assertIn(msg, response.message)

    def assert_note_equals(self, response, sender, recipient, message):
        self.assertEqual(sender, response.sender)
        self.assertEqual(recipient, response.recipient)
        self.assertIn(message, response.message)

    # Test client-side input checks
    def test_validate_request(self):
        client1 = client.Client()

        with NoPrint():
            # Request too long
            self.assertEqual(client1.validate_and_send_request('list|' + 'a' * 280), 1)

            # Nonexistent op
            self.assertEqual(client1.validate_and_send_request('hello|there'), 1)

            # Blank username
            self.assertEqual(client1.validate_and_send_request('create'), 1)
            self.assertEqual(client1.validate_and_send_request('login| '), 1)

            # Malformed chat
            self.assertEqual(client1.validate_and_send_request('send'), 1)
            self.assertEqual(client1.validate_and_send_request('send|bob'), 1)
            self.assertEqual(client1.validate_and_send_request('send|bob|  '), 1)

    # Tests basic functionality of creating an account
    def test_create_account(self):
        client1 = client.Client()
        client1.channel = grpc.insecure_channel(f'{HOST}:{PORT}')
        client1.conn = chat_pb2_grpc.GreeterStub(client1.channel)

        # Create bob
        response = client1.conn.CreateAccount(chat_pb2.UserName(name='bob'))
        self.assert_response_equal(response, 0, 0, 'Account created! Logged in as bob.')

        # Another client attempts to create bob
        client2 = client.Client()
        client2.channel = grpc.insecure_channel(f'{HOST}:{PORT}')
        client2.conn = chat_pb2_grpc.GreeterStub(client1.channel)

        response = client1.conn.CreateAccount(chat_pb2.UserName(name='bob'))
        self.assert_response_equal(response, 1, 0, 'Unable to create account: This username is already taken.')

        # Delete for idempotency
        client1.conn.DeleteAccount(chat_pb2.UserName(name='bob'))

        client1.channel.close()
        client2.channel.close()

    # Simulates race condition where 100 users are simultaneously creating account with same username
    def test_create_race(self):
        num_clients = 100
        clients = [None] * num_clients
        results = [None] * num_clients
        threads = [None] * num_clients

        def create_bob(c, i):
            time.sleep(randint(10, 100) * 10 ** -9 * (num_clients - i) ** 3)
            response = c.conn.CreateAccount(chat_pb2.UserName(name='bob'))

            # Record if account creation was successful
            results[i] = 1 - response.status

        # Start 100 clients in diff threads
        for i in range(num_clients):
            clients[i] = client.Client()
            clients[i].channel = grpc.insecure_channel(f'{HOST}:{PORT}')
            clients[i].conn = chat_pb2_grpc.GreeterStub(clients[i].channel)

            threads[i] = threading.Thread(target=create_bob, args=(clients[i], i))
            threads[i].start()

        for i in range(num_clients):
            threads[i].join()

        # Only one client should have succeeded in creating the account
        self.assertEqual(1, sum(results))
        # print(results)

        # Delete for idempotency
        clients[results.index(1)].conn.DeleteAccount(chat_pb2.UserName(name='bob'))

        for i in range(num_clients):
            clients[i].channel.close()

    # Test basic login functionality
    def test_login(self):

        # Create bob and alice
        client0 = client.Client()
        client0.channel = grpc.insecure_channel(f'{HOST}:{PORT}')
        client0.conn = chat_pb2_grpc.GreeterStub(client0.channel)
        client0.conn.CreateAccount(chat_pb2.UserName(name='alice'))

        client1 = client.Client()
        client1.channel = grpc.insecure_channel(f'{HOST}:{PORT}')
        client1.conn = chat_pb2_grpc.GreeterStub(client1.channel)
        client1.conn.CreateAccount(chat_pb2.UserName(name='bob'))
        client1.conn.Disconnect(chat_pb2.UserName(name='bob'))

        # Login bob
        client1 = client.Client()
        client1.channel = grpc.insecure_channel(f'{HOST}:{PORT}')
        client1.conn = chat_pb2_grpc.GreeterStub(client1.channel)
        response = client1.conn.Login(chat_pb2.UserName(name='bob'))
        self.assert_response_equal(response, 0, 0, 'Logged in as bob.')

        # Attempt to login alice on same client
        client1.name = 'bob'
        response = client1.conn.Login(chat_pb2.UserName(name='alice'))
        self.assertEqual(response.status, 1)

        # Attempt login invalid user
        client2 = client.Client()
        client2.channel = grpc.insecure_channel(f'{HOST}:{PORT}')
        client2.conn = chat_pb2_grpc.GreeterStub(client2.channel)
        response = client2.conn.Login(chat_pb2.UserName(name='nick'))

        self.assert_response_equal(response, 1, 0, 'Unable to login: This username does not exist. If you would like to use this username, please create a new account.')

        # Attempt to log into bob even though he's active already
        response = client2.conn.Login(chat_pb2.UserName(name='bob'))
        self.assertEqual(response.status, 1)

        # Delete for idempotency
        client0.conn.DeleteAccount(chat_pb2.UserName(name='alice'))
        client1.conn.DeleteAccount(chat_pb2.UserName(name='bob'))

        client0.channel.close()
        client1.channel.close()
        client2.channel.close()

    # Simulates race condition where 100 users are simultaneously logging into the same account
    def test_login_race(self):
        # create one bob
        client0 = client.Client()
        client0.channel = grpc.insecure_channel(f'{HOST}:{PORT}')
        client0.conn = chat_pb2_grpc.GreeterStub(client0.channel)
        client0.conn.CreateAccount(chat_pb2.UserName(name='bob'))
        client0.conn.Disconnect(chat_pb2.UserName(name='bob'))

        num_clients = 100
        clients = [None] * num_clients
        results = [None] * num_clients
        threads = [None] * num_clients

        def login_bob(c, i):
            time.sleep(randint(10, 100) * 10 ** -9 * (num_clients - i) ** 3)
            response = c.conn.Login(chat_pb2.UserName(name='bob'))

            # Record if account creation was successful
            results[i] = 1 - response.status

        # Start 100 clients in diff threads
        for i in range(num_clients):
            clients[i] = client.Client()
            clients[i].channel = grpc.insecure_channel(f'{HOST}:{PORT}')
            clients[i].conn = chat_pb2_grpc.GreeterStub(clients[i].channel)

            threads[i] = threading.Thread(target=login_bob, args=(clients[i], i))
            threads[i].start()

        for i in range(num_clients):
            threads[i].join()

        # Only one client should have succeeded in creating the account
        self.assertEqual(1, sum(results))
        # print(results)

        # Delete for idempotency
        clients[results.index(1)].conn.DeleteAccount(chat_pb2.UserName(name='bob'))

        for i in range(num_clients):
            clients[i].channel.close()

    # Test listing all account and wildcard filter
    def test_list_accounts(self):
        names = ['alice', 'bob', 'ashley', 'patrick']

        for name in names:
            c = client.Client()
            c.channel = grpc.insecure_channel(f'{HOST}:{PORT}')
            c.conn = chat_pb2_grpc.GreeterStub(c.channel)
            c.conn.CreateAccount(chat_pb2.UserName(name=name))
            c.conn.Disconnect(chat_pb2.UserName(name=name))

        response = c.conn.ListAccounts(chat_pb2.String(message=""))

        # List all accounts
        self.assert_response_equal(response, 0, 0, '\n- alice\n- bob\n- ashley\n- patrick\n')

        # List by wildcard
        response = c.conn.ListAccounts(chat_pb2.String(message="a*"))
        self.assert_response_equal(response, 0, 0, '\n- alice\n- ashley\n')

        # Delete for idempotency
        for name in names:
            c.conn.Login(chat_pb2.UserName(name=name))
            time.sleep(0.01)  # Need to sleep to mimic time it takes a client to actually type this
            c.conn.DeleteAccount(chat_pb2.UserName(name=name))
            time.sleep(0.01)

        c.channel.close()

    # Test deleting accounts
    def test_delete_account(self):
        c = client.Client()
        c.channel = grpc.insecure_channel(f'{HOST}:{PORT}')
        c.conn = chat_pb2_grpc.GreeterStub(c.channel)

        # Attempt delete before login
        with NoPrint():
            self.assertEqual(c.validate_and_send_request('delete|bob'), 1)

        # Create and delete
        c.conn.CreateAccount(chat_pb2.UserName(name='bob'))
        response = c.conn.DeleteAccount(chat_pb2.UserName(name='bob'))

        self.assert_response_equal(response, 0, 0, 'Account bob has been deleted. You are now logged out.')

        # Check account is actually deleted
        response = c.conn.Login(chat_pb2.UserName(name='bob'))
        self.assert_response_equal(response, 1, 0, 'Unable to login: This username does not exist. If you would like to use this username, please create a new account.')

        c.channel.close()

    # Test invalid chat inputs
    def test_send_chat_invalid(self):
        # Attempt to send message before logged in
        c1 = client.Client()
        c1.channel = grpc.insecure_channel(f'{HOST}:{PORT}')
        c1.conn = chat_pb2_grpc.GreeterStub(c1.channel)
        with NoPrint():
            self.assertEqual(c1.validate_and_send_request('send|alice|hi'), 1)

        c2 = client.Client()
        c2.channel = grpc.insecure_channel(f'{HOST}:{PORT}')
        c2.conn = chat_pb2_grpc.GreeterStub(c2.channel)
        c2.conn.CreateAccount(chat_pb2.UserName(name='bob'))
        response = c2.conn.SendNote(chat_pb2.Note(sender='bob', message='hello', recipient="ashley"))
        self.assert_response_equal(response, 1, 0, 'ERROR: Recipient username cannot be found.\n')

        # Attempt to send message to oneself
        with NoPrint():
            self.assertEqual(c2.validate_and_send_request('send|bob|hi'), 1)

        # Delete for idempotency
        c2.conn.DeleteAccount(chat_pb2.UserName(name='bob'))
        c2.channel.close()

    # Sending chat to someone who is logged in
    def test_send_chat_live(self):
        # Create bob, alice, and eve
        client0 = client.Client()
        client0.channel = grpc.insecure_channel(f'{HOST}:{PORT}')
        client0.conn = chat_pb2_grpc.GreeterStub(client0.channel)
        client0.conn.CreateAccount(chat_pb2.UserName(name='bob'))

        client1 = client.Client()
        client1.channel = grpc.insecure_channel(f'{HOST}:{PORT}')
        client1.conn = chat_pb2_grpc.GreeterStub(client1.channel)
        client1.conn.CreateAccount(chat_pb2.UserName(name='alice'))

        client2 = client.Client()
        client2.channel = grpc.insecure_channel(f'{HOST}:{PORT}')
        client2.conn = chat_pb2_grpc.GreeterStub(client2.channel)
        client2.conn.CreateAccount(chat_pb2.UserName(name='eve'))

        # Send messages to bob live
        response = client2.conn.SendNote(chat_pb2.Note(sender='eve', recipient='bob', message='hi'))
        self.assert_response_equal(response, 0, 1, '')

        # send messages to eve live
        response = client2.conn.SendNote(chat_pb2.Note(sender='bob', recipient='eve', message='hi'))
        self.assert_response_equal(response, 0, 1, '')

        # Delete for idempotency
        client0.conn.DeleteAccount(chat_pb2.UserName(name='alice'))
        client1.conn.DeleteAccount(chat_pb2.UserName(name='bob'))
        client2.conn.DeleteAccount(chat_pb2.UserName(name='eve'))

        client0.channel.close()
        client1.channel.close()
        client2.channel.close()

    # Queueing messages to someone inactive
    def test_send_chat_queue(self):
        # Create bob, alice, and eve
        client0 = client.Client()
        client0.channel = grpc.insecure_channel(f'{HOST}:{PORT}')
        client0.conn = chat_pb2_grpc.GreeterStub(client0.channel)
        client0.conn.CreateAccount(chat_pb2.UserName(name='bob'))

        client1 = client.Client()
        client1.channel = grpc.insecure_channel(f'{HOST}:{PORT}')
        client1.conn = chat_pb2_grpc.GreeterStub(client1.channel)
        client1.conn.CreateAccount(chat_pb2.UserName(name='alice'))

        client2 = client.Client()
        client2.channel = grpc.insecure_channel(f'{HOST}:{PORT}')
        client2.conn = chat_pb2_grpc.GreeterStub(client2.channel)
        client2.conn.CreateAccount(chat_pb2.UserName(name='eve'))

        # Queue messages to bob
        client2.conn.SendNote(chat_pb2.Note(sender='eve', recipient='bob', message='hi'))
        time.sleep(0.01)  # so that order is deterministic
        client1.conn.SendNote(chat_pb2.Note(sender='alice', recipient='bob', message='hi, you are cute'))

        msgs = client0.conn.ChatStream(chat_pb2.UserName(name='bob'))
        first = True
        for note in msgs:
            if first:
                self.assertEqual(note.message, 'hi')
                first = False
            else:
                self.assertEqual(note.message, 'hi, you are cute')
                break


        # Delete for idempotency
        client0.conn.DeleteAccount(chat_pb2.UserName(name='alice'))
        client1.conn.DeleteAccount(chat_pb2.UserName(name='bob'))
        client2.conn.DeleteAccount(chat_pb2.UserName(name='eve'))

        client0.channel.close()
        client1.channel.close()
        client2.channel.close()

    # Simulates race condition where 100 users are simultaneously sending message to the same account
    def test_queue_msg_race(self):
        client0 = client.Client()
        client0.channel = grpc.insecure_channel(f'{HOST}:{PORT}')
        client0.conn = chat_pb2_grpc.GreeterStub(client0.channel)
        client0.conn.CreateAccount(chat_pb2.UserName(name='bob'))

        num_clients = 100
        clients = [None] * num_clients
        results = [None] * num_clients
        threads = [None] * num_clients

        def create_client_send_msg(c, i):
            time.sleep(randint(10, 100) * 10 ** -9 * (num_clients - i) ** 3)
            response = c.conn.SendNote(chat_pb2.Note(sender='eve', recipient='bob', message='hi'))

            # Record if message was successful
            results[i] = 1 - response.status

        # Create 100 diff accounts
        for i in range(num_clients):
            clients[i] = client.Client()
            clients[i].channel = grpc.insecure_channel(f'{HOST}:{PORT}')
            clients[i].conn = chat_pb2_grpc.GreeterStub(clients[i].channel)

            threads[i] = threading.Thread(target=create_client_send_msg, args=(clients[i], i))
            threads[i].start()

        # Send msgs in diff threads at same time
        for i in range(num_clients):
            threads[i] = threading.Thread(target=create_client_send_msg, args=(clients[i], i))
            threads[i].start()

        for i in range(num_clients):
            threads[i].join()

        # All clients should have succeeded
        self.assertEqual(num_clients, sum(results))

        # Delete for idempotency
        # Delete for idempotency
        client0.conn.DeleteAccount(chat_pb2.UserName(name='bob'))

        for i in range(num_clients):
            clients[i].channel.close()


class NoPrint(object):
    def __init__(self, stdout=None, stderr=None):
        self.devnull = open(os.devnull, 'w')
        self._stdout = stdout or self.devnull or sys.stdout
        self._stderr = stderr or self.devnull or sys.stderr

    def __enter__(self):
        self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
        self.old_stdout.flush();
        self.old_stderr.flush()
        sys.stdout, sys.stderr = self._stdout, self._stderr

    def __exit__(self, exc_type, exc_value, traceback):
        self._stdout.flush();
        self._stderr.flush()
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr
        self.devnull.close()


if __name__ == '__main__':
    unittest.main()