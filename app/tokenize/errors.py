from abc import ABC, abstractmethod
from typing import Generic, TypeVar

ValueT = TypeVar("ValueT")

class BaseError(ABC, Generic[ValueT]):
    __slots__ = ["line_num", "value"]
    msg_format: str
        
    def __init__(self, line_num: int, value: ValueT) -> None:
        self.line_num = line_num
        self.value = value
    
    def __str__(self) -> str:
        return f"[line: {self.line_num}] " + self.msg_format.format(self.value)


class UnexpectedCharacterError(BaseError[str]):
    msg_format = "Error: Unexpected character: {}"