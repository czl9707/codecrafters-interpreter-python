from argparse import ArgumentParser, Namespace
import sys
from typing import Iterator

from ..helper.bi_direction_iterator import BiDirectionIterator

from .no_op import Comments, WhiteSpace
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
    
    def __iter__(self) -> Iterator[Symbol]:
        while not self.iter.EOF:
            if Comments.consume_comments(self.iter):
                continue
            if WhiteSpace.consume_white_space(self.iter):
                continue
            
            if sym := Symbol.from_iter(self.iter):
                yield sym
            else:
                self.error = True
                print(UnexpectedCharacterError(1, next(self.iter)), file=sys.stderr)
                
        yield EOFSymbol()
        
        
        