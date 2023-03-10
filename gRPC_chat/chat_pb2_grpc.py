# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import chat_pb2 as chat__pb2


class GreeterStub(object):
    """The greeting service definition.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ValidateUser = channel.unary_unary(
                '/chat.Greeter/ValidateUser',
                request_serializer=chat__pb2.UserName.SerializeToString,
                response_deserializer=chat__pb2.UserValidation.FromString,
                )
        self.ChatStream = channel.unary_stream(
                '/chat.Greeter/ChatStream',
                request_serializer=chat__pb2.UserName.SerializeToString,
                response_deserializer=chat__pb2.Note.FromString,
                )
        self.SendNote = channel.unary_unary(
                '/chat.Greeter/SendNote',
                request_serializer=chat__pb2.Note.SerializeToString,
                response_deserializer=chat__pb2.Response.FromString,
                )
        self.ListAccounts = channel.unary_unary(
                '/chat.Greeter/ListAccounts',
                request_serializer=chat__pb2.String.SerializeToString,
                response_deserializer=chat__pb2.Response.FromString,
                )
        self.DeleteAccount = channel.unary_unary(
                '/chat.Greeter/DeleteAccount',
                request_serializer=chat__pb2.UserName.SerializeToString,
                response_deserializer=chat__pb2.Response.FromString,
                )
        self.CreateAccount = channel.unary_unary(
                '/chat.Greeter/CreateAccount',
                request_serializer=chat__pb2.UserName.SerializeToString,
                response_deserializer=chat__pb2.Response.FromString,
                )
        self.Login = channel.unary_unary(
                '/chat.Greeter/Login',
                request_serializer=chat__pb2.UserName.SerializeToString,
                response_deserializer=chat__pb2.Response.FromString,
                )
        self.Disconnect = channel.unary_unary(
                '/chat.Greeter/Disconnect',
                request_serializer=chat__pb2.UserName.SerializeToString,
                response_deserializer=chat__pb2.Response.FromString,
                )


class GreeterServicer(object):
    """The greeting service definition.
    """

    def ValidateUser(self, request, context):
        """Sends a greeting
        rpc SayHello (HelloRequest) returns (HelloReply) {}
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ChatStream(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendNote(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ListAccounts(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteAccount(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CreateAccount(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Login(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Disconnect(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_GreeterServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'ValidateUser': grpc.unary_unary_rpc_method_handler(
                    servicer.ValidateUser,
                    request_deserializer=chat__pb2.UserName.FromString,
                    response_serializer=chat__pb2.UserValidation.SerializeToString,
            ),
            'ChatStream': grpc.unary_stream_rpc_method_handler(
                    servicer.ChatStream,
                    request_deserializer=chat__pb2.UserName.FromString,
                    response_serializer=chat__pb2.Note.SerializeToString,
            ),
            'SendNote': grpc.unary_unary_rpc_method_handler(
                    servicer.SendNote,
                    request_deserializer=chat__pb2.Note.FromString,
                    response_serializer=chat__pb2.Response.SerializeToString,
            ),
            'ListAccounts': grpc.unary_unary_rpc_method_handler(
                    servicer.ListAccounts,
                    request_deserializer=chat__pb2.String.FromString,
                    response_serializer=chat__pb2.Response.SerializeToString,
            ),
            'DeleteAccount': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteAccount,
                    request_deserializer=chat__pb2.UserName.FromString,
                    response_serializer=chat__pb2.Response.SerializeToString,
            ),
            'CreateAccount': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateAccount,
                    request_deserializer=chat__pb2.UserName.FromString,
                    response_serializer=chat__pb2.Response.SerializeToString,
            ),
            'Login': grpc.unary_unary_rpc_method_handler(
                    servicer.Login,
                    request_deserializer=chat__pb2.UserName.FromString,
                    response_serializer=chat__pb2.Response.SerializeToString,
            ),
            'Disconnect': grpc.unary_unary_rpc_method_handler(
                    servicer.Disconnect,
                    request_deserializer=chat__pb2.UserName.FromString,
                    response_serializer=chat__pb2.Response.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'chat.Greeter', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Greeter(object):
    """The greeting service definition.
    """

    @staticmethod
    def ValidateUser(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chat.Greeter/ValidateUser',
            chat__pb2.UserName.SerializeToString,
            chat__pb2.UserValidation.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ChatStream(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/chat.Greeter/ChatStream',
            chat__pb2.UserName.SerializeToString,
            chat__pb2.Note.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SendNote(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chat.Greeter/SendNote',
            chat__pb2.Note.SerializeToString,
            chat__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ListAccounts(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chat.Greeter/ListAccounts',
            chat__pb2.String.SerializeToString,
            chat__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DeleteAccount(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chat.Greeter/DeleteAccount',
            chat__pb2.UserName.SerializeToString,
            chat__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def CreateAccount(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chat.Greeter/CreateAccount',
            chat__pb2.UserName.SerializeToString,
            chat__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Login(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chat.Greeter/Login',
            chat__pb2.UserName.SerializeToString,
            chat__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Disconnect(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chat.Greeter/Disconnect',
            chat__pb2.UserName.SerializeToString,
            chat__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
