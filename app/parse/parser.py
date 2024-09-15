import sys
from typing import Iterator, Optional

from ..utils import ParserBaseError
from ..tokens import Tokenizer, EOFSymbol, SemicolonSymbol
from ..expressions import Expression

class Parser:
    def __init__(self, s:str) -> None:
        self.tokenizer = Tokenizer(s)
        self.self_error = False
    
    @property
    def error(self) -> bool:
        return self.self_error or self.tokenizer.error
    
    def __iter__(self) -> Iterator[Expression]:
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
                        yield expression
                    expression = None
                    continue
                
                if expression and expression._statement:
                    expression.right = Expression.from_token(token, expression.right, token_iter)
                else:
                    expression = Expression.from_token(token, expression, token_iter)
            
            if expression:
                yield expression
        except ParserBaseError as e:
            e.line_num = self.tokenizer.line
            print(e, file=sys.stderr)
            self.self_error = True