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
    
    tokenized = Tokenizer(file_contents)
    for token in tokenized:
        print(token)
    
    if tokenized.error:
        exit(65)
    


class Tokenizer:
    def __init__(self, s: str) -> None:
        self.s = s
        self.error = False
    
    def __iter__(self) -> Iterator[Symbol]:
        s_length = len(self.s)
        start = 0
        end = start + 1
        
        while start < s_length:
            end = start + 1
            while end <= s_length:
                if Symbol.is_symbol(self.s[start: end]):
                    if end == s_length:
                        yield Symbol.from_string(self.s[start: end])
                        start = end
                        break
                    else:
                        end += 1
                        continue
            
                if (start + 1 == end):
                    self.error = True
                    print(UnexpectedCharacterError(1, self.s[start]), file=sys.stderr)
                    start = end
                    break
                else:
                    yield Symbol.from_string(self.s[start: end - 1])
                    start = end - 1
                    break
        
        yield EOFSymbol()
        
        
        