
from abc import ABC, abstractmethod
from typing import Type, Union

from .errors import UnexpectedCharacterError, UnterminatedStringError
from .character_provider import CharacterProvider

from ..expressions import Expression, LiteralExpression
    

class Token(ABC):
    __slots__ = ["literal", "token_type", "lexeme"]
    _type2symbol_class: dict[str, Type['Symbol']] = {}
    _type2reserved_class: dict[str, Type['ReservedWord']] = {}

    token_type: str
    lexeme: str
    literal: str
    
    @staticmethod
    def is_symbol(cp: CharacterProvider) -> bool:
        for l in range(2, 0, -1):
            if cp.top(l) in Token._type2symbol_class:
                return True
        return False

    @staticmethod
    def is_reserved_word(cp: CharacterProvider) -> bool:
        for l in range(6, 1, -1):
            if cp.top(l) in Token._type2reserved_class:
                return True
        return False
            
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
        elif Token.is_reserved_word(cp):
            return ReservedWord.from_iter(cp)
        elif Token.is_string_literal(cp):
            return StringLiteral.from_iter(cp)
        elif Token.is_number_literal(cp):
            return NumberLiteral.from_iter(cp)
        elif Token.is_identifier(cp):
            return Identifier.from_iter(cp)

        raise UnexpectedCharacterError(cp.line, cp.forward())
    
    def __str__(self) -> str:
        return f"{self.token_type} {self.lexeme} {self.literal}"

    @abstractmethod
    def as_expression(self) -> Expression:
        ...

class NotImplementedExpressionToken(Token):
    def as_expression(self) -> Expression:
        raise NotImplementedError()
    
class LiteralToken(Token, ABC):
    def as_expression(self) -> LiteralExpression:
        return LiteralExpression(self)


class Identifier(NotImplementedExpressionToken, Token):
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
    

class StringLiteral(LiteralToken):
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


class NumberLiteral(LiteralToken):
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
        

class Symbol(Token, ABC):
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


class ReservedWord(Token, ABC):
    literal = "null"
    
    @classmethod
    def __init_subclass__(cls: Type["ReservedWord"]) -> None:
        Token._type2reserved_class[cls.lexeme] = cls
    
    @classmethod
    def from_iter(cls, cp: CharacterProvider) -> "ReservedWord":
        for l in range(6, 1, -1):
            sym = cp.top(l)
            if cp.top(l) in Token._type2reserved_class:
                return Token._type2reserved_class[cp.forward(len(sym))]()
        
        raise Exception("What the hack are you doing")


class LeftBraceSymbol(NotImplementedExpressionToken, Symbol):
    token_type = "LEFT_BRACE"
    lexeme = "{"
    
class RightBraceSymbol(NotImplementedExpressionToken, Symbol):
    token_type = "RIGHT_BRACE"
    lexeme = "}"
    
class LeftParenthesisSymbol(NotImplementedExpressionToken, Symbol):
    token_type = "LEFT_PAREN"
    lexeme = "("
    
class RightParenthesisSymbol(NotImplementedExpressionToken, Symbol):
    token_type = "RIGHT_PAREN"
    lexeme = ")"
    
class StarSymbol(NotImplementedExpressionToken, Symbol):
    token_type = "STAR"
    lexeme = "*" 
    
class DotSymbol(NotImplementedExpressionToken, Symbol):
    token_type = "DOT"
    lexeme = "." 
    
class CommaSymbol(NotImplementedExpressionToken, Symbol):
    token_type = "COMMA"
    lexeme = "," 
    
class PlusSymbol(NotImplementedExpressionToken, Symbol):
    token_type = "PLUS"
    lexeme = "+" 

class MinusSymbol(NotImplementedExpressionToken, Symbol):
    token_type = "MINUS"
    lexeme = "-" 

class SemicolonSymbol(NotImplementedExpressionToken, Symbol):
    token_type = "SEMICOLON"
    lexeme = ";" 
    
class EqualSymbol(NotImplementedExpressionToken, Symbol):
    token_type = "EQUAL"
    lexeme = "=" 
    
class EqualEqualSymbol(NotImplementedExpressionToken, Symbol):
    token_type = "EQUAL_EQUAL"
    lexeme = "==" 
    
class BangSymbol(NotImplementedExpressionToken, Symbol):
    token_type = "BANG"
    lexeme = "!"

class BangEqualSymbol(NotImplementedExpressionToken, Symbol):
    token_type = "BANG_EQUAL"
    lexeme = "!="
    
class LessSymbol(NotImplementedExpressionToken, Symbol):
    token_type = "LESS"
    lexeme = "<"

class LessEqualSymbol(NotImplementedExpressionToken, Symbol):
    token_type = "LESS_EQUAL"
    lexeme = "<="

class GreaterSymbol(NotImplementedExpressionToken, Symbol):
    token_type = "GREATER"
    lexeme = ">"

class GreaterEqualSymbol(NotImplementedExpressionToken, Symbol):
    token_type = "GREATER_EQUAL"
    lexeme = ">="

class SlashSymbol(NotImplementedExpressionToken, Symbol):
    token_type = "SLASH"
    lexeme = "/"
    
class EOFSymbol(NotImplementedExpressionToken, Symbol):
    token_type = "EOF"
    lexeme = ""
    
class AndReservedWord(NotImplementedExpressionToken, ReservedWord):
    token_type = "AND"
    lexeme = "and"

class ClassReservedWord(NotImplementedExpressionToken, ReservedWord):
    token_type = "CLASS"
    lexeme = "class"

class ElseReservedWord(NotImplementedExpressionToken, ReservedWord):
    token_type = "ELSE"
    lexeme = "else"

class FalseReservedWord(LiteralToken, ReservedWord):
    token_type = "FALSE"
    lexeme = "false"

class TrueReservedWord(LiteralToken, ReservedWord):
    token_type = "TRUE"
    lexeme = "true"

class NilReservedWord(LiteralToken, ReservedWord):
    token_type = "NIL"
    lexeme = "nil"

class ForReservedWord(NotImplementedExpressionToken, ReservedWord):
    token_type = "FOR"
    lexeme = "for"

class FunReservedWord(NotImplementedExpressionToken, ReservedWord):
    token_type = "FUN"
    lexeme = "fun"

class IfReservedWord(NotImplementedExpressionToken, ReservedWord):
    token_type = "IF"
    lexeme = "if"

class OrReservedWord(NotImplementedExpressionToken, ReservedWord):
    token_type = "OR"
    lexeme = "or"

class PrintReservedWord(NotImplementedExpressionToken, ReservedWord):
    token_type = "PRINT"
    lexeme = "print"

class ReturnReservedWord(NotImplementedExpressionToken, ReservedWord):
    token_type = "RETURN"
    lexeme = "return"

class SuperReservedWord(NotImplementedExpressionToken, ReservedWord):
    token_type = "SUPER"
    lexeme = "super"

class ThisReservedWord(NotImplementedExpressionToken, ReservedWord):
    token_type = "THIS"
    lexeme = "this"

class VarReservedWord(NotImplementedExpressionToken, ReservedWord):
    token_type = "VAR"
    lexeme = "var"

class WhileReservedWord(NotImplementedExpressionToken, ReservedWord):
    token_type = "WHILE"
    lexeme = "while"

