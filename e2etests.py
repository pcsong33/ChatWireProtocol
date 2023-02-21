import unittest
import client

# TO RUN THESE TESTS, YOU MUST 1) run server.py, 2) change HOST to match the host of the server, and finally 3) run python e2etests.py

HOST = 'dhcp-10-250-203-22.harvard.edu'

def unpack_server_response(response):
    return {'status': ord(response[0]), 'is_chat': int(response[1]), 'msg': response[2:]}

class ChatAppTest(unittest.TestCase):
    def test_create_account(self):
        client1 = client.Client(host=HOST)
        client1.s.connect((client1.host, client1.port))

        client1.pack_and_send_request('create|bob')

        response = unpack_server_response(client1.s.recv(1024).decode())
        self.assertEqual(response['status'], 0)
        self.assertEqual(response['is_chat'], 0)
        self.assertEqual(response['msg'], 'Account created! Logged in as bob.')

        client1.s.close()

    # def setUp(self):
    #     self.server = 
    #     self.server_thread = threading.Thread(target=self.server.serve_forever)
    #     # self.client = socket.create_connection((HOST, PORT))
    #     # self.server_thread.setDaemon(True)
    #     self.server_thread.start()

    # def tearDown(self):
    #     # self.client.close()
    #     # self.server.shutdown()

if __name__ == '__main__':
    unittest.main()