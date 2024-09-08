from abc import ABC
from argparse import ArgumentParser, Namespace
from typing import Type


SYMBOLS = {
    "{":"LEFT_BRACE",
    "}":"RIGHT_BRACE",
    "(":"LEFT_PAREN",
    ")":"RIGHT_PAREN",
}

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
    def from_chr(cls, ch: str) -> "Symbol":
        return Symbol._chr2symbol[ch]()
    
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
    
    
class EOFSymbol(Symbol):
    symbol = ""
    name = "EOF"
    

def config_tokenize_parser(arg_parser: ArgumentParser) -> None:
    arg_parser.add_argument("file")
    arg_parser.set_defaults(entry=tokenize)


def tokenize(ns: Namespace) -> None:
    with open(ns.file) as fd:
        file_contents = fd.read()

    it = iter(file_contents)
    for char in it:
        if not Symbol.is_symbol(char):
            raise NotImplementedError()
        
        sym = Symbol.from_chr(char)
    
        print(sym)
    
    print(EOFSymbol())    
    