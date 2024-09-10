
from abc import ABC
from typing import Optional, Type

from ..helper.bi_direction_iterator import BiDirectionIterator


class Symbol(ABC):
    __slots__ = ["value"]
    _chr2symbol: dict[str, Type['Symbol']] = {}
    
    symbol: str
    name: str
    
    @classmethod
    def __init_subclass__(cls: Type["Symbol"]) -> None:
        Symbol._chr2symbol[cls.symbol] = cls
    
    @staticmethod
    def is_symbol(symbol: str) -> bool:
        return symbol in Symbol._chr2symbol
    
    @classmethod
    def from_iter(cls, iter: BiDirectionIterator) -> Optional["Symbol"]:
        sym = next(iter)
        sym += next(iter)
        if Symbol.is_symbol(sym):
            pass
        elif Symbol.is_symbol(sym[0]):
            sym = sym[0]
            iter.step_back()
        else:
            iter.step_back()
            iter.step_back()
            return None
        
        return Symbol._chr2symbol[sym]()
        
    
    def __str__(self) -> str:
        return f"{self.name} {self.symbol} null"


class LeftBraceSymbol(Symbol):
    symbol = "{"
    name = "LEFT_BRACE"
    
class RightBraceSymbol(Symbol):
    symbol = "}"
    name = "RIGHT_BRACE"
    
class LeftParenthesisSymbol(Symbol):
    symbol = "("
    name = "LEFT_PAREN"
    
class RightParenthesisSymbol(Symbol):
    symbol = ")"
    name = "RIGHT_PAREN"
    
class StarSymbol(Symbol):
    symbol= "*" 
    name="STAR"
    
class DotSymbol(Symbol):
    symbol= "." 
    name="DOT"
    
class CommaSymbol(Symbol):
    symbol= "," 
    name="COMMA"
    
class PlusSymbol(Symbol):
    symbol= "+" 
    name="PLUS"

class MinusSymbol(Symbol):
    symbol= "-" 
    name="MINUS"

class SemicolonSymbol(Symbol):
    symbol= ";" 
    name="SEMICOLON"
    
class EqualSymbol(Symbol):
    symbol= "=" 
    name="EQUAL"
    
class EqualEqualSymbol(Symbol):
    symbol= "==" 
    name="EQUAL_EQUAL"
    
class BangSymbol(Symbol):
    symbol = "!"
    name = "BANG"

class BangEqualSymbol(Symbol):
    symbol = "!="
    name = "BANG_EQUAL"
    
class LessSymbol(Symbol):
    symbol = "<"
    name = "LESS"

class LessEqualSymbol(Symbol):
    symbol = "<="
    name = "LESS_EQUAL"

class GreaterSymbol(Symbol):
    symbol = ">"
    name = "GREATER"

class GreaterEqualSymbol(Symbol):
    symbol = ">="
    name = "GREATER_EQUAL"

    
class EOFSymbol(Symbol):
    symbol = ""
    name = "EOF"
    
