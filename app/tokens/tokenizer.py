import sys
from typing import Iterator

from .character_provider import CharacterProvider

from ..utils import TokenizerBaseError
from .tokens import Token, EOFSymbol


class Tokenizer:
    def __init__(self, s: str) -> None:
        self.cp = CharacterProvider(s)
        self.error = False
    
    @property
    def line(self) -> int:
        return self.cp.line
    
    def __iter__(self) -> Iterator[Token]:
        while not self.cp.EOF:
            # print("DEBUG: " self.cp.s[self.cp.index:])
            
            if self.__forward_until_next_valid():
                continue
            try:
                yield Token.from_iter(self.cp)
            except TokenizerBaseError as e:
                self.error = True
                print(e, file=sys.stderr)
                
        yield EOFSymbol()
        
    # return value: consumed any characters
    def __forward_until_next_valid(self) -> bool:
        # comments
        if self.cp.top(2) == "//":            
            self.cp.forward_until("\n")
            return True
        
        # white spaces
        elif self.cp.top().isspace():
            while self.cp.top().isspace():
                self.cp.forward()
            
            return True
        
        return False
        
        