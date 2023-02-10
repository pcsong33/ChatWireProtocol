
# CS262 Engineering Notebook | Ashley Zhuang & Patrick Song

## 2/9/2023

We started by creating a very bare bones application that allows the server and a client to send messages to each other. It is a little bit buggy at this point, as the client can only send messages when the server has sent one before, and also the client can't send messages at all once the server has already previously connected with a client. We also currently have the host name hardcoded because since the host name was different across our different devices, so we'll have to investigate that further.

We realized though that since the specs ask for multiple users to be able to chat with one another, it likely makes the not sense to restructure our application such that the server is not chatting at all, but rather serves to pass messages between the clients (who are the "users"). 

This probably requires threading, so that the server can accept multiple connections (?). Since we are rewriting most of the code, some of these bugs may not be applicable anymore, but we'll see.

Next steps (brainstorm):
* Investigate why host name is appearing differently.
* Re-write code so that multiple clients can connect to server.
* For queue-ing messages for clients: keep a dictionary where key = existing username, value = (boolean connected, array [(message, sender)])
* When delivering an undelivered message, first check if the sender is in the dictionary, in case their account has been deleted.
* How to receive messages in a continuous stream? Right now not sure how to receive multiple messages without sending messages in between.