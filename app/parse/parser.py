import sys
from typing import Iterator, Optional

from ..execution import ExecutionContext, ExecutionScope
from ..utils import ParserBaseError, MissingScopeExpressionError
from ..tokens import Tokenizer, EOFSymbol, SemicolonSymbol, LeftBraceSymbol, RightBraceSymbol
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
        expression: Optional[Expression] = None
    
        try:
            for token in token_iter:
                # print("DEBUG: " + str(token))

                if token.__class__ == EOFSymbol:
                    break
                if token.__class__ == SemicolonSymbol:
                    if expression:
                        # print("DEBUG: " + str(expression))
                        yield (self.context.current_scope, expression)
                    expression = None
                    continue
                if token.__class__ == LeftBraceSymbol:
                    self.context.push_scope()
                    continue
                if token.__class__ == RightBraceSymbol:
                    self.context.pop_scope()
                    continue
                
                if expression and expression._statement:
                    expression.right = Expression.from_token(token, expression.right, token_iter)
                else:
                    expression = Expression.from_token(token, expression, token_iter)
            
            if expression:
                yield (self.context.current_scope, expression)

            if self.context.current_scope is not self.context.root_scope:
                raise MissingScopeExpressionError(self.tokenizer.line)
        except ParserBaseError as e:
            e.line_num = self.tokenizer.line
            print(e, file=sys.stderr)
            self.self_error = True