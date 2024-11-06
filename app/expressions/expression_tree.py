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
        token_iter: Iterator['Token']
    ) -> None:
        assert prev_expr is None
        self.children = []
        
        assert token.lexeme == "{"
        token = next(token_iter)
        while token:
            if token.lexeme == "}":
                return
            
            self.children.append(
                Expression.from_iter_till_end(token, token_iter)
            )
            token = next(token_iter)
        
        raise MissingScopeExpressionError()

                
    def __str__(self) -> str:
        return "\n".join([
            "entering scope",
            *[str(exp) for exp in self.children],
            "leaving scope",
        ])
    
    def evaluate(self, scope: 'ExecutionScope') -> None:
        scope = scope.create_child_scope()
        for child in self.children:
            child.evaluate(scope)


# passing in dummy token to avoid { as the first token
class RootExpressionTree(ExpressionTree):
    __slots__=["children"]
    children: list[Expression]
    
    def __init__(
        self, 
        token: 'Token', # dummy token
        prev_expr: Optional['Expression'], 
        token_iter: Iterator['Token']
    ) -> None:
        assert prev_expr is None
        self.children = []
        
        token = next(token_iter)
        while token:
            if token.token_type == "EOF":
                return
            
            self.children.append(
                Expression.from_iter_till_end(token, token_iter)
            )
            token = next(token_iter)
        
        raise MissingScopeExpressionError()
    