from argparse import ArgumentParser, Namespace
import sys
from typing import Iterator

from ..helper.bi_direction_iterator import BiDirectionIterator

from .errors import UnexpectedCharacterError
from .symbols import Symbol, EOFSymbol

def config_tokenize_parser(arg_parser: ArgumentParser) -> None:
    arg_parser.add_argument("file")
    arg_parser.set_defaults(entry=print_tokens)

def print_tokens(ns: Namespace) -> None:
    with open(ns.file) as fd:
        file_contents = fd.read()
    
    tokenized = Tokenizer(file_contents)
    for token in tokenized:
        print(token)
    
    if tokenized.error:
        exit(65)
    


class Tokenizer:
    def __init__(self, s: str) -> None:
        self.iter = BiDirectionIterator(s)
        self.error = False
        self.line = 1
    
    def __iter__(self) -> Iterator[Symbol]:
        while not self.iter.EOF:
            # print(self.iter.s[self.iter.index:])
            if self.forward_until_next_valid():
                continue
            
            if sym := Symbol.from_iter(self.iter):
                yield sym
            else:
                self.error = True
                print(UnexpectedCharacterError(self.line, next(self.iter)), file=sys.stderr)
                
        yield EOFSymbol()
        
    # return value: consumed any characters
    def forward_until_next_valid(self) -> bool:
        s = next(self.iter)
        if not s.isspace() and s != "/":
            self.iter.step_back()
            return False

        # comments
        if s == "/":
            if self.iter.EOF:
                self.iter.step_back()
                return False
            
            s += next(self.iter)
            if s != "//":
                self.iter.step_back()
                self.iter.step_back()
                return False
            
            while not self.iter.EOF:
                if next(self.iter) == "\n":
                    self.iter.step_back()
                    
            return True
        
        # white spaces
        else:
            self.iter.step_back()
            while (s:= next(self.iter)).isspace():
                if s == "\n":
                    self.line += 1
            
            self.iter.step_back()
            return True
        
        