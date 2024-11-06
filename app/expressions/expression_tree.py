from typing import TYPE_CHECKING, Iterator, Optional, Type

from ..utils import MissingScopeExpressionError
from .expressions import StatementExpression, Expression

if TYPE_CHECKING:
    from ..tokens import Token
    from ..execution import ExecutionScope

"Scope token will generate a this guy"
class ExpressionTree(StatementExpression):
    __slots__=["children"]
    children: list[Expression]
    
    def __init__(
        self, 
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        iter: Iterator['Token']
    ) -> None:
        assert prev_expr is None
        self.children = []
        
        if token.lexeme == "{":
            token = next(iter)
        while token:
            # print("DEBUG: " + str(token))

            if token.token_type == "EOF" or token.lexeme == "}":
                return
            
            self.children.append(
                Expression.from_iter_till_end(token, iter)
            )
            token = next(iter)
        
        raise MissingScopeExpressionError()

                
    def __str__(self) -> str:
        return "\n".join([
            "entering scope",
            *[str(exp) for exp in self.children],
            "leaving scope",
        ])
    
    @classmethod
    def from_token(
        cls: Type['ExpressionTree'],
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        iter: Iterator['Token']
    ) -> 'ExpressionTree':
        return cls(token, prev_expr, iter)
    
    def evaluate(self, scope: 'ExecutionScope') -> None:
        scope = scope.create_child_scope()
        for child in self.children:
            child.evaluate(scope)
    
