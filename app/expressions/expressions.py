from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Iterator, Optional, Type, Union

from ..utils import MissingExpressionError

if TYPE_CHECKING:
    from ..tokens import Token

class Expression(ABC):
    _token2expression_map: dict[Type['Token'], Type['Expression']] = {}
    
    @abstractmethod
    def __init__(
        self, 
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        iter: Iterator['Token']
    ) -> None:
        ...
        
    @abstractmethod
    def __str__(self) -> str:
        ...
    
    @staticmethod
    def from_iter(
        iter: Iterator['Token'],
        prev_expr: Optional['Expression'],
    ):
        token = next(iter)
        return Expression.from_token(token, prev_expr, iter)
    
    @staticmethod
    @abstractmethod
    def from_token(
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        iter: Iterator['Token']
    ) -> 'Expression':
        if token.__class__ not in Expression._token2expression_map:
            raise MissingExpressionError(-1, token)
        
        return Expression._token2expression_map[token.__class__].from_token(token, prev_expr, iter)
    
    @classmethod
    def register(cls: Type['Expression'], token_cls: Type['Token']):
        Expression._token2expression_map[token_cls] = cls
        return token_cls


class LiteralExpression(Expression):
    __slots__= ["value"]
    value: 'Token'
    
    def __init__(
        self, 
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        iter: Iterator['Token']
    ) -> None:
        self.value = token
    
    def __str__(self) -> str:
        if self.value.literal == "null":
            return self.value.lexeme 
        return self.value.literal

    @staticmethod
    def from_token(
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        iter: Iterator['Token']
    ) -> "LiteralExpression":
        return LiteralExpression(token, prev_expr, iter)

class GroupExpression(Expression):
    __slots__ = ["expr"]
    expr: Optional[Expression]
    
    def __init__(
        self, 
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        iter: Iterator['Token']
    ) -> None:
        self.expr = None
        for token in iter:
            if token.lexeme == ")":
                break
            self.expr = Expression.from_token(token, self.expr, iter)
        
    def __str__(self) -> str:
        return f"(group {self.expr if self.expr else ''})"

    @staticmethod
    def from_token(
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        iter: Iterator['Token']
    ) -> "GroupExpression":
        return GroupExpression(token, prev_expr, iter)


class UnaryExpression(Expression):
    __slots__ = ["operator", "right"]
    operator: 'Token'
    right: 'Expression'

    def __init__(
        self, 
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        iter: Iterator['Token']
    ) -> None:
        self.operator = token
        self.right = Expression.from_iter(iter, None)

    def __str__(self) -> str:
        return f"({self.operator.lexeme} {self.right})"

    @staticmethod
    def from_token(
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        iter: Iterator['Token']
    ) -> "UnaryExpression":
        return UnaryExpression(token, prev_expr, iter)


class BinaryExpression(Expression):
    __slots__ = ["operator", "left", "right"]
    operator: 'Token'
    right: 'Expression'
    left: 'Expression'

    def __init__(
        self, 
        token: 'Token', 
        prev_expr: 'Expression', 
        iter: Iterator['Token']
    ) -> None:        
        self.operator = token
        self.left = prev_expr
        self.right = Expression.from_iter(iter, None)

    def __str__(self) -> str:
        return f"({self.operator.lexeme} {self.left} {self.right})"

    @staticmethod
    def from_token(
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        iter: Iterator['Token']
    ) -> "BinaryExpression":
        assert prev_expr is not None
        return BinaryExpression(token, prev_expr, iter)


class UnaryBinaryExpressionRouter(Expression, ABC):
    @staticmethod
    def from_token(
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        iter: Iterator['Token']
    ) -> Union[BinaryExpression, UnaryExpression]:
        if prev_expr is None:
            return UnaryExpression(token, None, iter)
        else:
            return BinaryExpression(token, prev_expr, iter)