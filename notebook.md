
# CS262 Engineering Notebook | Ashley Zhuang & Patrick Song


## 2/15/2023

Ensured that multiple logins cannot occur. If the same user tries to login when they are already connected to the server, the program will exit gracefully. I added a `.active` attribute to the client class to check for connection status. Also, did some code clean-up, moving code into main() functions for both client and server files.
1. Investigate why host name is appearing differently.
1. Check if the sender of queued msg is in the dictionary, in case their account has been deleted. 
1. ~~Ensure multiple logins to an account cannot occur.~~
1. Test the code a lottttt more, across multiple devices too. 
1. General code clean up and abstraction.



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
1. Re-write code so that multiple clients can connect to server.
1. For queue-ing messages for clients: keep a dictionary where key = existing username, value = (boolean connected, array [(message, sender)])
1. When delivering an undelivered message, first check if the sender is in the dictionary, in case their account has been deleted.
1. How to receive messages in a continuous stream? Right now not sure how to receive multiple messages without sending messages in between.