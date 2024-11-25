import sys
from typing import Iterator

from ..utils import ParserBaseError
from ..tokens import Tokenizer, EOFSymbol
from ..expressions import RootAST, Expression

class Parser:
    def __init__(self, s:str) -> None:
        self.tokenizer = Tokenizer(s)
        self._error = False
        try:
            token_iter = iter(self.tokenizer)
            self.ast = RootAST(
                EOFSymbol(), None, token_iter
            )
                    
        except ParserBaseError as e:
            print(f"[line {self.tokenizer.line}] {e}", file=sys.stderr)
            self._error = True
    
    @property
    def error(self) -> bool:
        return self._error or self.tokenizer.error
    
    def __iter__(self) -> Iterator[Expression]:
        for exp in self.ast.children:
            yield exp
