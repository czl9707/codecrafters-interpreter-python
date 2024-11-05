import sys
from typing import Iterator

from ..execution import ExecutionContext, ExecutionScope
from ..utils import ParserBaseError, MissingScopeExpressionError
from ..tokens import Tokenizer, EOFSymbol, LeftBraceSymbol, RightBraceSymbol
from ..expressions import Expression

class Parser:
    def __init__(self, s:str) -> None:
        self.tokenizer = Tokenizer(s)
        self.self_error = False
        self.context = ExecutionContext()
    
    @property
    def error(self) -> bool:
        return self.self_error or self.tokenizer.error
    
    def __iter__(self) -> Iterator[tuple[ExecutionScope, Expression]]:
        token_iter = iter(self.tokenizer)
    
        try:
            for token in token_iter:
                # print("DEBUG: " + str(token))

                if token.__class__ == EOFSymbol:
                    break
                if token.__class__ == LeftBraceSymbol:
                    self.context.push_scope()
                    continue
                if token.__class__ == RightBraceSymbol:
                    self.context.pop_scope()
                    continue
                
                expression = Expression.from_iter_till_semicolon(token, token_iter)
                yield (
                    self.context.current_scope,
                    expression,
                )
            
            if self.context.current_scope is not self.context.root_scope:
                raise MissingScopeExpressionError(self.tokenizer.line)
        except ParserBaseError as e:
            e.line_num = self.tokenizer.line
            print(e, file=sys.stderr)
            self.self_error = True