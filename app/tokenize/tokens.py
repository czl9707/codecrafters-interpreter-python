
from abc import ABC
from typing import Type

from .errors import UnexpectedCharacterError
from .character_provider import CharacterProvider


class Token(ABC):
    __slots__ = ["literal", "token_type", "lexeme"]
    _type2symbol_class: dict[str, Type['Symbol']] = {}

    token_type: str
    lexeme: str
    literal: str

    
    @staticmethod
    def is_symbol(symbol: str) -> bool:
        return symbol in Token._type2symbol_class
    
    @classmethod
    def from_iter(cls, cp: CharacterProvider) -> "Token":
        sym = ""
        while not cp.EOF and len(sym) < 2:
            sym += next(cp)

        while sym:
            if Token.is_symbol(sym):
                return Token._type2symbol_class[sym]()
            
            cp.step_back()
            sym = sym[:-1]
        
        ch = next(cp)
        raise UnexpectedCharacterError(cp.line, ch)
    
    def __str__(self) -> str:
        return f"{self.token_type} {self.lexeme} {self.literal}"


class Symbol(Token):
    literal = "null"
    
    @classmethod
    def __init_subclass__(cls: Type["Symbol"]) -> None:
        Token._type2symbol_class[cls.token_type] = cls


class LeftBraceSymbol(Symbol):
    token_type = "{"
    lexeme = "LEFT_BRACE"
    
class RightBraceSymbol(Symbol):
    token_type = "}"
    lexeme = "RIGHT_BRACE"
    
class LeftParenthesisSymbol(Symbol):
    token_type = "("
    lexeme = "LEFT_PAREN"
    
class RightParenthesisSymbol(Symbol):
    token_type = ")"
    lexeme = "RIGHT_PAREN"
    
class StarSymbol(Symbol):
    token_type = "*" 
    lexeme = "STAR"
    
class DotSymbol(Symbol):
    token_type = "." 
    lexeme = "DOT"
    
class CommaSymbol(Symbol):
    token_type = "," 
    lexeme = "COMMA"
    
class PlusSymbol(Symbol):
    token_type = "+" 
    lexeme = "PLUS"

class MinusSymbol(Symbol):
    token_type = "-" 
    lexeme = "MINUS"

class SemicolonSymbol(Symbol):
    token_type = ";" 
    lexeme = "SEMICOLON"
    
class EqualSymbol(Symbol):
    token_type = "=" 
    lexeme = "EQUAL"
    
class EqualEqualSymbol(Symbol):
    token_type = "==" 
    lexeme = "EQUAL_EQUAL"
    
class BangSymbol(Symbol):
    token_type = "!"
    lexeme = "BANG"

class BangEqualSymbol(Symbol):
    token_type = "!="
    lexeme = "BANG_EQUAL"
    
class LessSymbol(Symbol):
    token_type = "<"
    lexeme = "LESS"

class LessEqualSymbol(Symbol):
    token_type = "<="
    lexeme = "LESS_EQUAL"

class GreaterSymbol(Symbol):
    token_type = ">"
    lexeme = "GREATER"

class GreaterEqualSymbol(Symbol):
    token_type = ">="
    lexeme = "GREATER_EQUAL"

class SlashSymbol(Symbol):
    token_type = "/"
    lexeme = "SLASH"
    
class EOFSymbol(Symbol):
    token_type = ""
    lexeme = "EOF"
    
