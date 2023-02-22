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
    * Keeps a global dictionary of `ClientModel` objects, to keep track of all of the accounts created, socket connections, queued messages, etc.
* `client.py` - Defines the `Client` class.
    * Connects to the server.
    * Runs a background thread to listen for and print messages from the server.
    * Takes in requests from the user via command-line input, which is packaged according to the wire protocol and sent to the server.
* `tests.py` - Unit tests. To run the tests, you must 1) run `server.py`, 2) change `HOST` in `tests.py` to match the server, and finally 3) run `python3 tests.py`
    * The tests spawn `Client` objects connected to the server. These objects send requests to the server within the tests, and the tests check whether the responses from the server are as expected.

## gRPC Chat Application