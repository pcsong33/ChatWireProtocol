from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ClientRequest(_message.Message):
    __slots__ = ["op"]
    class OpType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    CREATE: ClientRequest.OpType
    DELETE: ClientRequest.OpType
    EXIT: ClientRequest.OpType
    LIST: ClientRequest.OpType
    LOGIN: ClientRequest.OpType
    OP_FIELD_NUMBER: _ClassVar[int]
    SEND: ClientRequest.OpType
    op: ClientRequest.OpType
    def __init__(self, op: _Optional[_Union[ClientRequest.OpType, str]] = ...) -> None: ...

class Empty(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class MessageStatus(_message.Message):
    __slots__ = ["status"]
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    CREATE: MessageStatus.Status
    DELETE: MessageStatus.Status
    EXIT: MessageStatus.Status
    LIST: MessageStatus.Status
    LOGIN: MessageStatus.Status
    SEND: MessageStatus.Status
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: MessageStatus.Status
    def __init__(self, status: _Optional[_Union[MessageStatus.Status, str]] = ...) -> None: ...

class Note(_message.Message):
    __slots__ = ["message", "recipient", "sender"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_FIELD_NUMBER: _ClassVar[int]
    SENDER_FIELD_NUMBER: _ClassVar[int]
    message: str
    recipient: str
    sender: str
    def __init__(self, sender: _Optional[str] = ..., recipient: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class String(_message.Message):
    __slots__ = ["message"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class UserName(_message.Message):
    __slots__ = ["name"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class UserValidation(_message.Message):
    __slots__ = ["message"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: bool
    def __init__(self, message: bool = ...) -> None: ...
