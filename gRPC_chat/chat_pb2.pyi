from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Empty(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class Note(_message.Message):
    __slots__ = ["message", "recipient", "sender"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_FIELD_NUMBER: _ClassVar[int]
    SENDER_FIELD_NUMBER: _ClassVar[int]
    message: str
    recipient: str
    sender: str
    def __init__(self, sender: _Optional[str] = ..., recipient: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class Response(_message.Message):
    __slots__ = ["message", "sender", "status"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    SENDER_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    message: str
    sender: int
    status: int
    def __init__(self, message: _Optional[str] = ..., status: _Optional[int] = ..., sender: _Optional[int] = ...) -> None: ...

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
