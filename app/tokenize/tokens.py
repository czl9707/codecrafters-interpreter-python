
from abc import ABC
from typing import Type, Optional, Union

from .errors import UnexpectedCharacterError, UnterminatedStringError
from .character_provider import CharacterProvider


class Token(ABC):
    __slots__ = ["literal", "token_type", "lexeme"]
    _type2symbol_class: dict[str, Type['Symbol']] = {}

    token_type: str
    lexeme: str
    literal: str

    
    @staticmethod
    def is_symbol(cp: CharacterProvider) -> bool:
        return (
            cp.top() in Token._type2symbol_class or 
            cp.top(2) in Token._type2symbol_class
        )
            
    @staticmethod
    def is_identifier(cp: CharacterProvider) -> bool:
        return cp.top().isalnum() or cp.top() == "_"
    
    @staticmethod
    def is_string_literal(cp: CharacterProvider) -> bool:
        return cp.top() == "\""
    
    @staticmethod
    def is_number_literal(cp: CharacterProvider) -> bool:
        return cp.top().isdigit()
    
    
    @classmethod
    def from_iter(cls, cp: CharacterProvider) -> "Token":
        if Token.is_symbol(cp):
            return Symbol.from_iter(cp)
        elif Token.is_string_literal(cp):
            return StringLiteral.from_iter(cp)
        elif Token.is_number_literal(cp):
            return NumberLiteral.from_iter(cp)
        elif Token.is_identifier(cp):
            return Identifier.from_iter(cp)

        raise UnexpectedCharacterError(cp.line, cp.forward())
    
    def __str__(self) -> str:
        return f"{self.token_type} {self.lexeme} {self.literal}"

class Identifier(Token):
    token_type = "IDENTIFIER"
    literal = "null"
     
    def __init__(self, value: str) -> None:
        self.lexeme = value
    
    @staticmethod
    def __valid_char(ch: str) -> bool:
        return ch.isalnum() or ch == "_"

    @classmethod
    def from_iter(cls, cp: CharacterProvider) -> "Identifier":
        if not Identifier.__valid_char(cp.top()):
            raise Exception("What the hack are you doing")
        
        s = ""
        while Identifier.__valid_char(cp.top()):
            s += cp.forward()
        
        return Identifier(s)
    

class StringLiteral(Token):
    token_type = "STRING"
    def __init__(self, value: str) -> None:
        self.literal = value
        self.lexeme = '"' + value + '"'
    
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
    def __init__(self, str_expression: str, value: Union[int, float]) -> None:
        self.lexeme = str_expression
        self.literal = str(float(value))
    
    @classmethod
    def from_iter(cls, cp: CharacterProvider) -> "NumberLiteral":
        if not cp.top().isdigit():
            raise Exception("What the hack are you doing")

        num = ""
        while cp.top().isdigit():
            num += cp.forward()
            
        if cp.top() != ".":
            return NumberLiteral(num, int(num))
        
        num += cp.forward() # "."
        
        while cp.top().isdigit():
            num += cp.forward()
        
        return NumberLiteral(num, float(num))
        

class Symbol(Token):
    literal = "null"
    
    @classmethod
    def __init_subclass__(cls: Type["Symbol"]) -> None:
        Token._type2symbol_class[cls.lexeme] = cls

    @classmethod
    def from_iter(cls, cp: CharacterProvider) -> "Symbol":
        for l in range(2, 0, -1):
            sym = cp.top(l)
            if cp.top(l) in Token._type2symbol_class:
                return Token._type2symbol_class[cp.forward(len(sym))]()
        
        raise Exception("What the hack are you doing")

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
    
