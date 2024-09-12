
from abc import ABC
from typing import Type, Optional

from .errors import UnexpectedCharacterError, UnterminatedStringError
from .character_provider import CharacterProvider


class Token(ABC):
    __slots__ = ["literal", "token_type", "lexeme"]
    _type2symbol_class: dict[str, Type['Symbol']] = {}

    token_type: str
    lexeme: str
    literal: str

    
    @staticmethod
    def is_symbol(symbol: str) -> bool:
        if not symbol: 
            return False
        
        return symbol in Token._type2symbol_class
    
    @classmethod
    def from_iter(cls, cp: CharacterProvider) -> "Token":
        for l in range(2, 0, -1):
            sym = cp.top(l)
            if Token.is_symbol(sym):
                cp.forward(len(sym))
                return Token._type2symbol_class[sym]()

        raise UnexpectedCharacterError(cp.line, cp.forward())
    
    def __str__(self) -> str:
        return f"{self.token_type} {self.lexeme} {self.literal}"


class StringLiteral(Token):
    token_type = "STRING"
    def __init__(self, value: str) -> None:
        self.literal = value
        self.lexeme = '"' + value + '"'
    
    @staticmethod
    def is_string_literal(cp: CharacterProvider) -> bool:
        return cp.top() == "\""
    
    @classmethod
    def from_iter(cls, cp: CharacterProvider) -> "StringLiteral":
        if cp.top() != "\"":
            raise Exception("What the hack are you doing")
        
        cp.forward()
        line_num = cp.line
        s = cp.forward_until("\"")
        if s[-1] != "\"":
            raise UnterminatedStringError(line_num, None)
        
        else:
            return StringLiteral(s[:-1])

class NumberLiteral(Token):
    token_type = "NUMBER"
    def __init__(self, integer: str, decimal: Optional[str] = None) -> None:
        self.lexeme = integer + ("." + decimal if decimal else "")
        self.literal = integer + "." + (decimal if decimal else "0")
    
    @staticmethod
    def is_number_literal(cp: CharacterProvider) -> bool:
        return cp.top().isdigit()
    
    @classmethod
    def from_iter(cls, cp: CharacterProvider) -> "NumberLiteral":
        if not cp.top().isdigit():
            raise Exception("What the hack are you doing")

        integer = ""
        while (ch:=cp.forward()).isdigit():
            integer += ch
        
        if ch != ".":
            cp.backward()
            decimal = None
        else:
            decimal = ""
            while (ch:=cp.forward()).isdigit():
                decimal += ch
            cp.backward()            
            
        return NumberLiteral(integer, decimal)
        

class Symbol(Token):
    literal = "null"
    
    @classmethod
    def __init_subclass__(cls: Type["Symbol"]) -> None:
        Token._type2symbol_class[cls.lexeme] = cls


class LeftBraceSymbol(Symbol):
    token_type = "LEFT_BRACE"
    lexeme = "{"
    
class RightBraceSymbol(Symbol):
    token_type = "RIGHT_BRACE"
    lexeme = "}"
    
class LeftParenthesisSymbol(Symbol):
    token_type = "LEFT_PAREN"
    lexeme = "("
    
class RightParenthesisSymbol(Symbol):
    token_type = "RIGHT_PAREN"
    lexeme = ")"
    
class StarSymbol(Symbol):
    token_type = "STAR"
    lexeme = "*" 
    
class DotSymbol(Symbol):
    token_type = "DOT"
    lexeme = "." 
    
class CommaSymbol(Symbol):
    token_type = "COMMA"
    lexeme = "," 
    
class PlusSymbol(Symbol):
    token_type = "PLUS"
    lexeme = "+" 

class MinusSymbol(Symbol):
    token_type = "MINUS"
    lexeme = "-" 

class SemicolonSymbol(Symbol):
    token_type = "SEMICOLON"
    lexeme = ";" 
    
class EqualSymbol(Symbol):
    token_type = "EQUAL"
    lexeme = "=" 
    
class EqualEqualSymbol(Symbol):
    token_type = "EQUAL_EQUAL"
    lexeme = "==" 
    
class BangSymbol(Symbol):
    token_type = "BANG"
    lexeme = "!"

class BangEqualSymbol(Symbol):
    token_type = "BANG_EQUAL"
    lexeme = "!="
    
class LessSymbol(Symbol):
    token_type = "LESS"
    lexeme = "<"

class LessEqualSymbol(Symbol):
    token_type = "LESS_EQUAL"
    lexeme = "<="

class GreaterSymbol(Symbol):
    token_type = "GREATER"
    lexeme = ">"

class GreaterEqualSymbol(Symbol):
    token_type = "GREATER_EQUAL"
    lexeme = ">="

class SlashSymbol(Symbol):
    token_type = "SLASH"
    lexeme = "/"
    
class EOFSymbol(Symbol):
    token_type = "EOF"
    lexeme = ""
    
