import datetime
from typing import Any, Iterator, Optional, Self, Type, TYPE_CHECKING, Callable

from ..tokens.tokens import NilReservedWord, Token
from .expressions import FunctiontDefinitionExpression, Expression

if TYPE_CHECKING:
    from ..execution import ExecutionScope

class BuiltInFunctionDefinitionExpression(FunctiontDefinitionExpression):
    name: str
    parameters: list[str]
    body: Expression
    closure: 'ExecutionScope'
    
    @classmethod
    def from_token(
        cls: Type[Self],
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        token_iter: Iterator['Token']
    ) -> Self:
        raise NotImplementedError()

    def __init__(
        self, 
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        token_iter: Iterator['Token']
    ) -> None:
        pass

class ExpressionMixin:
    __slots__ = ["evaluate"]
    def __init__(self, callback: Callable[['ExecutionScope'], Any]):
        self.evaluate = callback
                

def define_built_in_function(name: str, paramters: list[str], callback: Callable[['ExecutionScope'], Any], root_scope: 'ExecutionScope') -> BuiltInFunctionDefinitionExpression:
    expression = BuiltInFunctionDefinitionExpression(NilReservedWord(), None, iter([]))
    expression.name = name
    expression.parameters = paramters
    expression.closure = root_scope
    expression.body = ExpressionMixin(callback)  # type: ignore
    
    return expression
