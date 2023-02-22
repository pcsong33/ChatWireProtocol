## 2/17/2023

We started by following the gRPC python tutorial from the [official docs](https://grpc.io/docs/languages/python/basics/). Throughout the process, we learned how the pb2 files are built from the proto files. In the proto file, we can define certain type restraints and specify the return behavior of functions. After running the build command, python classes are built in the pv2 files, enforcing the rules specified in the proto file. 

The following are possible next steps:

1. Currently, the server is able to connect to the client on an insecure port. We need to see if there is a hostname equivalent in gRPC that we can connect to.
2. Fill in the `receive_msgs`, `on_new_clients`, etc. equivalents into the gRPC version of the code. Also, we need to investigate the [bi-directional streaming](https://grpc.io/docs/languages/python/basics/#bidirectional-streaming-rpc) form gRPC, as this will be useful for message sending/receiving and has a slightly different setup that the normal client server setup in the ChatWireProtocol code.
3. Have been using this link as a reference, may be useful to refer to as we continue to make changes: https://melledijkstra.github.io/science/chatting-with-grpc-in-python
4. Can you create an account when you are logged in?
5. List when no accounts have been created
6. exit gracefully?