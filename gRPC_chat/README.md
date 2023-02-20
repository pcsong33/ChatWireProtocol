## Building Changes
When making changes to the chat.proto file, run the following command to update the pb2 python files: 

`% python -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. chat.proto`
