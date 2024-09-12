from argparse import ArgumentParser, Namespace
import sys
from typing import Iterator

from .character_provider import CharacterProvider

from .errors import BaseTokenizeError
from .tokens import NumberLiteral, StringLiteral, Token, EOFSymbol

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
        self.cp = CharacterProvider(s)
        self.error = False
    
    def __iter__(self) -> Iterator[Token]:
        while not self.cp.EOF:
            # print(self.cp.s[self.cp.index:])
            
            if self.forward_until_next_valid():
                continue
            try:
                if StringLiteral.is_string_literal(self.cp):
                    yield StringLiteral.from_iter(self.cp)
                elif NumberLiteral.is_number_literal(self.cp):
                    yield NumberLiteral.from_iter(self.cp)
                else:
                    yield Token.from_iter(self.cp)
            except BaseTokenizeError as e:
                self.error = True
                print(e, file=sys.stderr)
                
        yield EOFSymbol()
        
    # return value: consumed any characters
    def forward_until_next_valid(self) -> bool:
        # comments
        if self.cp.top(2) == "//":            
            while not self.cp.EOF:
                if self.cp.forward() == "\n":
                    self.cp.backward()
                    break
                    
            return True
        
        # white spaces
        elif self.cp.top().isspace():
            while not self.cp.EOF:
                if not self.cp.forward().isspace():
                    self.cp.backward()
                    break
            
            return True
        
        return False
        
        