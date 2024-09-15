from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..expressions import Expression
    from ..tokens import Token


class BaseError(ABC, BaseException):
    line_num: int
    
    def __init__(self, line_num: int) -> None:
        self.line_num = line_num
    
    @abstractmethod
    def __str__(self) -> str:
        return f"[line {self.line_num}] "

class TokenizerBaseError(BaseError, ABC):
    def __str__(self) -> str:
        return super().__str__() + "Error: "


class UnexpectedCharacterError(TokenizerBaseError):
    def __init__(self, line_num: int, ch: str) -> None:
        super().__init__(line_num)
        self.ch = ch
    
    def __str__(self) -> str:
        return super().__str__() + f"Unexpected character: {self.ch}"
    
class UnterminatedStringError(TokenizerBaseError):
    def __str__(self) -> str:
        return super().__str__() + "Unterminated string."

    
class ParserBaseError(BaseError, ABC):
    def __init__(self, line_num: int, token: 'Token') -> None:
        super().__init__(line_num)
        self.token = token
        
    def __str__(self) -> str:
        return super().__str__() + f"Error at '{self.token.lexeme}': "
    
class MissingExpressionError(ParserBaseError):
    def __str__(self) -> str:
        return super().__str__() + "Expect expression."
    

class RuntimeError(BaseError, ABC):
    msg: str
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