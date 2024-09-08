from argparse import ArgumentParser, Namespace
import sys
from typing import Iterator

from .errors import UnexpectedCharacterError
from .symbols import Symbol, EOFSymbol

def config_tokenize_parser(arg_parser: ArgumentParser) -> None:
    arg_parser.add_argument("file")
    arg_parser.set_defaults(entry=print_tokens)

def print_tokens(ns: Namespace) -> None:
    with open(ns.file) as fd:
        file_contents = fd.read()
    
    for token in Tokenizer(file_contents):
        print(token)
    


class Tokenizer:
    def __init__(self, s: str) -> None:
        self.s = s
        self.error = False
    
    def __iter__(self) -> Iterator[Symbol]:
        sym: Symbol = EOFSymbol()
        start = 0
        end = start + 1
        
        while end <= len(self.s):
            if Symbol.is_symbol(self.s[start: end]):
                sym = Symbol.from_string(self.s[start: end])
                end += 1
                continue
            
            if (start + 1 == end):
                ch = self.s[start]
                print(UnexpectedCharacterError(1, ch), file=sys.stderr)
                start = end
                end = start + 1
            else:
                start = end - 1
                end = start + 1
                yield sym
                sym = EOFSymbol()
        
        yield sym
                
        
        
        