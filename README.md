# CS262 Chat Application

## Wire Protocol Chat Application
This application is located in the `wire_protocol_chat/` directory.

### Usage Instructions
To run this application, do the following:
1. Start up the server on a device by running `python3 server.py`.
1. Change the `HOST` variable in `client.py` to match the server (the first thing printed when you run the server).
1. Start up a client by running `python3 client.py` on another device. You can now use the application to chat with other clients.

### Wire Protocol
Requests from a client to the server are sent in the form `[operation]|[paramaters]` (encoded with UTF-8), where the parameters are delimited with pipes as well. The request must be less than 280 characters. Here is the list of valid operations:
* Op 1 - Create account. Parameter: username. Ex: `1|alice`.
* Op 2 - Log into existing account. Parameter: username. Ex: `2|alice`.
* Op 3 - Send a message to another account. Parameters: recipient's username, message. Ex: `3|bob|hello there`.
* Op 4 - List accounts, or subset of accounts via Unix shell-style wildcard. Parameter: wildcard (optional, no wildcard = all accounts listed). Ex: `4|a*`.
* Op 5 - Delete the account. Ex: `5`.
* Op 6 - Exit the chat application. Ex: `6`.

Responses from the server to a client are sent in the form `[message length][status][indicator][message]` (encoded with UTF-8). The first two values are given as unicode characters, so that the first three values form a 3-byte long header for the message. Here are the specs for the header and message values:
* Message length: This is the number of bytes in the message, not including the header.
* Status: This indicates the status of a server (non-chat) message. Possible statuses:
    * 0 = Success
    * 1 = Error
    * 2 = Note from server
* Indicator: This indicates whether this is a chat message from another client or a message directly from the server. The value is 0 if it is a server message and 1 if the message is a chat message.
* Message: The message is any string. If it is a chat message (so if the indicator is 1), then the message must be in the form of `[sender]|[chat message]`.


### File Overview
* `server.py` - Defines the `Server` class. 
    * Accepts connections from multiple clients, with a new thread being started for each one. 
    * Listens to requests from the clients, and responds accordingly with messages following the wire protocol. 
    * Passes chat messages between clients.
    * Keeps a global dictionary of `User` objects, to keep track of all of the accounts created, socket connections, queued messages, etc.
* `client.py` - Defines the `Client` class.
    * Connects to the server.
    * Runs a background thread to listen for and print messages from the server.
    * Takes in requests from the user via command-line input, which is packaged according to the wire protocol and sent to the server.
* `tests.py` - Unit tests. To run the tests, you must 1) run `server.py`, 2) change `HOST` in `tests.py` to match the server, and finally 3) run `python3 tests.py`
    * The tests spawn `Client` objects connected to the server. These objects send requests to the server within the tests, and the tests check whether the responses from the server are as expected.
    * If a `Too many open files` error is received when running tests, run `ulimit -n 2048` to reconfigure the maximum number of open files.

## gRPC Chat Application
This application is located in the `gRPC_chat/` directory. 

### Usage Instructions
Running the gRPC chat application requires the installation of two gRPC packages. The instructions for 
installing the packages in a virtual environment are list below

#### Creating a virtual environment
To create a virtual environment, run the following command:

`python -m venv venv`

This will create a new directory called `venv`. To activate the virtual environment, run

`source venv/bin/activatev`

With the virtual environment activated, install the gRPC packages by running the command:

`pip install grpcio grpcio-tools`

#### Running the application
To run this application, do the following:
1. Start up the server on a device by running `python3 server.py`.
1. Change the `HOST` variable in `client.py` to match the server (the first thing printed when you run the server).
1. Start up a client by running `python3 client.py` on another device. You can now use the application to chat with other clients.

### gRPC Protocol Buffer

The protocol buffer, defined in the `chat.proto`, defines four types of messages.
* Note: Used to deliver messages in client-server and server-client communication.
* Response: Used to deliver error and status messages from the server to the client.
* UserName: Account verification object. Client-side message to server.
* String: Account listing object. Client-side message to server.

The Response object mirrors the wire protocol server-client response message, containing analogous fields
with the same specs described above for the wire protocol:
* Status
* Sender (analogous to indicator in the wire protocol)
* Message

The Note, UserName, and String objects are largely used as inputs to gRPC server functions. 
This is one differentiation from the wire protocol implementation; in the gRPC implementation, 
message parsing is done client-side, and different server functions are called based on user input.

### File Overview
The file structure for gRPC follows the WireProtocol structure closely. Functions unique to the gRPC application or described below.
* `server.py` - Defines the `Server` class. 
    * Accepts connections from multiple clients, with a new thread being started for each one. 
    * Listens to requests from the clients, and responds accordingly. The following functions are defined for and called by the client based on the client request:
      * `ChatStream`
      * `SendNote` 
      * `ListAccounts` 
      * `DeleteAccount` 
      * `CreateAccount` 
      * `Login` 
      * `Disconnect`
    * Passes chat messages between clients.
    * Keeps a global dictionary of `ClientModel` objects, to keep track of all the accounts created, socket connections, queued messages, etc.
* `client.py` - Defines the `Client` class.
    * Connects to the server.
    * Runs a background thread to listen for and print messages from the server.
    * Takes in requests from the user via command-line input, which is parsed client-side and sent to the server based on the specific message.
* `tests.py` - Unit tests. To run the tests, you must 1) run `server.py`, 2) change `HOST` in `tests.py` to match the server, and finally 3) run `python3 tests.py`
    * The tests spawn `Client` objects connected to the server. These objects send requests to the server within the tests, and the tests check whether the responses from the server are as expected.
    * If a `Too many open files` error is received when running tests, run `ulimit -n 2048` to reconfigure the maximum number of open files.
