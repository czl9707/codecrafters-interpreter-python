from argparse import ArgumentParser, Namespace
import sys
from typing import Iterator

from .character_provider import CharacterProvider

from .errors import BaseTokenizeError
from .tokens import Token, EOFSymbol

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
                yield Token.from_iter(self.cp)
            except BaseTokenizeError as e:
                self.error = True
                print(e, file=sys.stderr)
                
        yield EOFSymbol()
        
    # return value: consumed any characters
    def forward_until_next_valid(self) -> bool:
        s = next(self.cp)
        if not s.isspace() and s != "/":
            self.cp.step_back()
            return False

        # comments
        if s == "/":
            if self.cp.EOF:
                self.cp.step_back()
                return False
            
            s += next(self.cp)
            if s != "//":
                self.cp.step_back(2)
                return False
            
            while not self.cp.EOF:
                if next(self.cp) == "\n":
                    break
                    
            return True
        
        # white spaces
        else:
            self.cp.step_back()
            while not self.cp.EOF and (s:= next(self.cp)).isspace():
                pass
            self.cp.step_back()
            
            return True
        
        