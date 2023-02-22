
# CS262 Engineering Notebook

## Reflections
In this section, we note the differences in implementation and performance between the
gRPC and Wire Protocol versions of the chat application.
1. **Code Complexity**: The code structure for the gRPC and Wire Protocol implementations were largely similar. Both implementations made use of `Client`
and `Server` objects that organized the code into client and server-specific functions. The network implementation for both involved having the server stat a new thread for each client that would listen to requests, and responds accordingly with messages.
The client file would spin up a background thread to listen for and print messages from the server. However, the specific network implementation between the Wire Protocl and gRPC varied:
    * **Wire Protocol**: Network connection was coded using the `Socket` library in Python. Sockets are the endpoints of a bidirectional communications channel. Sockets support communications between two processes by acting as endpoints of a bidirectional communications channel. 
   Methods like `sendall()`, `bind()`, `accept()`, etc. are used to enable connection between processes in the code. The Wire Protocol defines a message structure that allows both the client and server to parse and output network communications.
    * **gRPC**: In gRPC, the client has generated stub functions that provide the same methods as the server. The client and server can then use stubs to interact with other. An example of 
   stub functions implemented in chat application are:
      * `ChatStream`
      * `SendNote` 
      * `ListAccounts` 
      * `DeleteAccount` 
      * `CreateAccount` 
      * `Login` 
      * `Disconnect`
   
      In the gRPC code, the client parses through a user input and sends a specific stub function based on the parsing.
2. **Performance Differences**: When comparing our suite of tests on the gRPC and Wire Protocol implementations, the Wire Protocol performed faster. The average speed of test completion over 10 tests are listed below:
   * **Wire Protocol**: .589 seconds 
   * **gRPC**: .989 seconds 
   
   * These performance differences are likely due to the fact that the Wire Protocol relies on socket level connections, which is much lower-level and requires
    less overhead than the gRPC model. While the Wire Protocol may be more efficient for shorter chat communications, gRPC will likely perform better when larger data formats are 
   being sent over the network, as gRPC's utilization of protocol buffers allows for fast parsing and accessing of data. Given that all chat messages were capped at 280 characters, our tests did not cover scenarios where the chat messages contained large amounts of data.
3. **Buffer Sizes**: For our wire protocol, the maximum incoming message from client to server size is 280 bytes, since messages are limited to 280 characters. Outgoing server-to-client messages again do not have a message limit, though the header is fixed at 3-bytes long. By default, the maximum incoming message size on gRPC is 4 mb. Outgoing server-to-client messages again do not have a message limit. 

## 2/21/2023
Final TODO list
* ~~make folders~~
* make readme
    * how to actually run the app + pip requirements for grpc
    * ~~what exactly is the wire protocol~~
    * file structure / high level overview of functions?
* docstrings
* combine notebooks
    * Add to your notebook comparisons over the complexity of the code, any performance differences, and the size of the buffers being sent back and forth between the client and the server. 
* grpc tests

## 2/21/2023
Finished writing unit tests for gRPC and performed some code cleanup as well. Next todos:
* finish readme
* finish notebook

## 2/21/2023
Finalized server functions and fixed an error where one of the queued messaged were not delivering correctly.
* `ChatStream`
* `SendNote` 
* `ListAccounts` 
* `DeleteAccount` 
* `CreateAccount` 
* `Login` 
* `Disconnect`


## 2/20/2023
* Made a fix so that when a client exits suddenly (e.g. ctrl c), the broken pipe error is caught and the client is disconnected.
* I had something weird happen where I got a ConnectionResetError, but I wasn't able to reproduce it.
    * I was able to reproduce this actually by sending a message from A to B and then exiting B abruptly, but I think I have fixed this error by catching ConnectionResetErrors, and also by adding a nested try-except block when a user A fails to send a message to user B who is presumably logged in and might've disconnected suddenly.
* I also added a success message when undelivered messages have been sent, in case the user exits suddenly and the messages are cleared before everything has actually been printed.
* Refactored all of the code so that the client and server files are classes now. 
* Wrote comprehensive end-to-end tests that test the functionality of the client-side request validations and the request-handling on the server-side.

## 2/19/2023
Following the wire protocol refactoring, I rewrote the gRPC to mirror much of the code structure. A few key differences are that messages are being fully parsed server-side.
While in the wire protocol, messages are "packed" and sent using the pipe syntax, in the gRPC code, client requests are parsed client-side, and server functions are called based on the input.
Some server functions that were implemented are listed below:
* `ChatStream`
* `SendNote` 
* `ValidateUser`

## 2/19/2023
I want to rewrite this so that the wire protocol is a lot cleaner and less prone to errors. Outline of what I'm thinking:

Client-side:
* Send message via [op]|[params]
* ops: 1 = create account (param: username), 2 = login (param: username), 3 = send message (params: recipient, username), 4 = list accounts (param: wildcard), 5 = delete account, 6 = exit

Server-side:
* Send message via [msg length][status code][indicator if chat/server msg][msg]
    * status: 0 = success, 1 = error, 2 = note from server
* Possible server messages
    * ~~Client is already active / logged in elsewhere~~
    * ~~Successfully connected~~
    * ~~Client's message is malformed - no op, or parameters are wrong~~
    * ~~Recipient username not found~~
    * ~~Attempting to send message to oneself~~
    * ~~Blank message~~
    * ~~Message is past character limit~~

## 2/17/2023
gRPC time! We started by following the gRPC python tutorial from the [official docs](https://grpc.io/docs/languages/python/basics/). Throughout the process, we learned how the pb2 files are built from the proto files. In the proto file, we can define certain type restraints and specify the return behavior of functions. After running the build command, python classes are built in the pv2 files, enforcing the rules specified in the proto file. 

The following are possible next steps:

1. Currently, the server is able to connect to the client on an insecure port. We need to see if there is a hostname equivalent in gRPC that we can connect to.
2. Fill in the `receive_msgs`, `on_new_clients`, etc. equivalents into the gRPC version of the code. Also, we need to investigate the [bi-directional streaming](https://grpc.io/docs/languages/python/basics/#bidirectional-streaming-rpc) form gRPC, as this will be useful for message sending/receiving and has a slightly different setup that the normal client server setup in the ChatWireProtocol code.
3. Have been using this link as a reference, may be useful to refer to as we continue to make changes: https://melledijkstra.github.io/science/chatting-with-grpc-in-python

## 2/15/2023

Ensured that multiple logins cannot occur. If the same user tries to login when they are already connected to the server, the program will exit gracefully. I added a `.active` attribute to the client class to check for connection status. Also, did some code clean-up, moving code into main() functions for both client and server files.
1. ~~Investigate why host name is appearing differently.~~
1. ~~Check if the sender of queued msg is in the dictionary, in case their account has been deleted. ~~
1. ~~Ensure multiple logins to an account cannot occur.~~
1. Test the code a lottttt more, across multiple devices too. 
    1. ~~Character limits~~
    1. ~~Client dying~~
    1. ~~Queueing messages for the same client on diff threads (need locking?)~~
    1. ~~Search via text wildcard~~
    1. ~~Need to send message lengths in buffers? might also fix the time sleeping for queueing stuff~~
    1. ~~Message from someone who was deleted~~
1. ~~General code clean up and abstraction.~~
1. ~~Unit tests~~

## 2/12/2023

I've added the functionality for queueing messages when a user is away and then delivering them once they return! I've also added the ability to list and delete accounts. The specs are pretty much all satisfied at this point, but some improvements are still needed. Some next steps:
1. Investigate why host name is appearing differently.
1. Check if the sender of queued msg is in the dictionary, in case their account has been deleted. 
1. Ensure multiple logins to an account cannot occur.
1. Test the code a lottttt more, across multiple devices too. 
1. General code clean up and abstraction.

## 2/11/2023

I've rewritten the application using threading now. It's at a stage where multiple clients can connect to the server, but they can't send each other messages yet (rather than can send messages to the server, which is just printed out as of now). Still pretty stumped on how to send messages in a continuous stream but I'll investigate this next.

I'm also not sure why but I'm able to connect 7 clients (and probably more but I haven't tested beyond that), even though I've set the listen parameter to 5.

Another thing to keep in mind is later when testing is the 280 character limit.

Ah I think we can change the client dictionary to store the c_socket instead of the connected boolean. Also, I think I've solved the receiving messages continuously problem with a background thread for clients!

I've been able to implement it now such that clients can send messages to each other when they are both logged in, and they receive messages on demand. #2 and #5 on the next steps list from last time have been dealt with, but the others are still todos. 

## 2/9/2023

We started by creating a very bare bones application that allows the server and a client to send messages to each other. It is a little bit buggy at this point, as the client can only send messages when the server has sent one before, and also the client can't send messages at all once the server has already previously connected with a client. We also currently have the host name hardcoded because since the host name was different across our different devices, so we'll have to investigate that further.

We realized though that since the specs ask for multiple users to be able to chat with one another, it likely makes the not sense to restructure our application such that the server is not chatting at all, but rather serves to pass messages between the clients (who are the "users"). 

This probably requires threading, so that the server can accept multiple connections (?). Since we are rewriting most of the code, some of these bugs may not be applicable anymore, but we'll see.

Next steps (brainstorm):
1. Investigate why host name is appearing differently.
1. ~~Re-write code so that multiple clients can connect to server.~~
1. ~~For queue-ing messages for clients: keep a dictionary where key = existing username, value = (boolean connected, array [(message, sender)])~~
1. When delivering an undelivered message, first check if the sender is in the dictionary, in case their account has been deleted.
1. ~~How to receive messages in a continuous stream? Right now not sure how to receive multiple messages without sending messages in between.~~