from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..tokens import Token


class BaseError(ABC, BaseException):            
    pass

class TokenizerBaseError(BaseError, ABC):
    def __str__(self) -> str:
        return super().__str__() + "Error: "


class UnexpectedCharacterError(TokenizerBaseError):
    def __init__(self, ch: str) -> None:
        super().__init__()
        self.ch = ch
    
    def __str__(self) -> str:
        return super().__str__() + f"Unexpected character: {self.ch}"
    
class UnterminatedStringError(TokenizerBaseError):
    def __str__(self) -> str:
        return super().__str__() + "Unterminated string."

    
class ParserBaseError(BaseError, ABC):
    pass

class MissingExpressionError(ParserBaseError):
    def __init__(self, token: 'Token') -> None:
        self.token = token
        
    def __str__(self) -> str:
        return super().__str__() + f"Error at '{self.token.lexeme}': Expect expression."


class MissingScopeExpressionError(ParserBaseError):        
    def __str__(self) -> str:
        return super().__str__() + "Error at end: Expect '{' ."
    

class RuntimeError(BaseError):
    msg: str = "General RuntimeError"
    def __init__(self) -> None:
        super().__init__(1)
    
    def __str__(self) -> str:
        return self.msg + "\n" + super().__str__()
    

class NoneNumberOperandError(RuntimeError):
    msg = "Operands must be numbers."
    
class UnMatchedOprendError(RuntimeError):
    msg = "Operands must be two numbers or two strings."
    
class UndefinedVariableError(RuntimeError):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.msg = f"Undefined variable '{name}'."