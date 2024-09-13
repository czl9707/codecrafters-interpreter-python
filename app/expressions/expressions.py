from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..tokens import Token

class Expression(ABC):
    pass

class LiteralExpression(Expression):
    __slots__= ["value"]
    value: 'Token'
    
    def __init__(self, value: 'Token') -> None:
        self.value = value
    
    def __str__(self) -> str:
        if self.value.literal == "null":
            return self.value.lexeme 
        return self.value.literal