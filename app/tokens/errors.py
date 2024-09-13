from abc import ABC
from typing import Generic, TypeVar

ValueT = TypeVar("ValueT")

class BaseTokenizeError(ABC, Generic[ValueT], BaseException):
    __slots__ = ["line_num", "value"]
    msg_format: str
        
    def __init__(self, line_num: int, value: ValueT) -> None:
        self.line_num = line_num
        self.value = value
    
    def __str__(self) -> str:
        return f"[line {self.line_num}] Error: " + self.msg_format.format(self.value)


class UnexpectedCharacterError(BaseTokenizeError[str]):
    msg_format = "Unexpected character: {}"
    
class UnterminatedStringError(BaseTokenizeError[None]):
    msg_format = "Unterminated string."