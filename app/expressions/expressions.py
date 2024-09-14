from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Iterator, Optional, Type, Union

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
    
    @classmethod
    @abstractmethod
    def from_token(
        cls: Type['Expression'],
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        iter: Iterator['Token']
    ) -> 'Expression':
        if token.__class__ not in Expression._token2expression_map:
            raise MissingExpressionError(-1, token)
        
        return Expression._token2expression_map[token.__class__].from_token(token, prev_expr, iter)
    
    @abstractmethod
    def evaluate(self) -> Any:
        ...
    
    @classmethod
    def register(cls: Type['Expression'], token_cls: Type['Token']):
        Expression._token2expression_map[token_cls] = cls
        return token_cls


class LiteralExpression(Expression, ABC):
    __slots__= ["value"]
    value: 'Token'
    
    def __init__(
        self, 
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        iter: Iterator['Token']
    ) -> None:
        self.value = token
    
    @abstractmethod
    def __str__(self) -> str:
        ...

    @classmethod
    def from_token(
        cls: Type['LiteralExpression'],
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        iter: Iterator['Token']
    ) -> "LiteralExpression":
        return cls(token, prev_expr, iter)


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

    @classmethod
    def from_token(
        cls: Type['GroupExpression'],
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        iter: Iterator['Token']
    ) -> "GroupExpression":
        return cls(token, prev_expr, iter)

    def evaluate(self) -> Any:
        if self.expr:
            return self.expr.evaluate()
        else:
            return None


class UnaryExpression(Expression, ABC):
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

    @classmethod
    def from_token(
        cls: Type['UnaryExpression'],
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        iter: Iterator['Token']
    ) -> "UnaryExpression":
        return cls(token, prev_expr, iter)


class BinaryExpression(Expression, ABC):
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

    @classmethod
    def from_token(
        cls: Type['BinaryExpression'],
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        iter: Iterator['Token']
    ) -> "BinaryExpression":
        if not prev_expr:
            raise MissingExpressionError(-1, token)
        return cls(token, prev_expr, iter)


class MinusNegativeExpressionRouter(Expression, ABC):
    @staticmethod
    def from_token(
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        iter: Iterator['Token']
    ) -> Union['MinusExpression', 'NegativeExpression']:
        if prev_expr is None:
            return NegativeExpression(token, None, iter)
        else:
            return MinusExpression(token, prev_expr, iter)
        

# *********************************************** Literal ***********************************************
class StringLiteralExpression(LiteralExpression):
    def __str__(self) -> str:
        return self.value.literal
        
    def evaluate(self) -> str:
        return self.value.literal
       
        
class NumberLiteralExpression(LiteralExpression):
    def __str__(self) -> str:
        return self.value.literal
        
    def evaluate(self) -> Union[int, float]:
        if "." in self.value.lexeme:
            return float(self.value.lexeme)
        return int(self.value.lexeme)


class BooleanLiteralExpression(LiteralExpression):
    def __str__(self) -> str:
        return self.value.lexeme

    def evaluate(self) -> bool:
        return self.value.lexeme == "true"
    

class NilLiteralExpression(LiteralExpression):
    def __str__(self) -> str:
        return self.value.lexeme

    def evaluate(self) -> None:
        return None

# *********************************************** Unary ***********************************************
class NegativeExpression(UnaryExpression):
    def evaluate(self) -> Any:
        return - self.right.evaluate()


class BangExpression(UnaryExpression):
    def evaluate(self) -> bool:        
        return not self.right.evaluate()


# *********************************************** Binary ***********************************************
class PlusExpression(BinaryExpression):
    def evaluate(self) -> Any:        
        return self.left.evaluate() + self.right.evaluate() 
    
    
class MinusExpression(BinaryExpression):
    def evaluate(self) -> Any:        
        return self.left.evaluate() - self.right.evaluate() 
    
    
class DivideExpression(BinaryExpression):
    def evaluate(self) -> Any:        
        return self.left.evaluate() / self.right.evaluate() 
    
    
class MultiplyExpression(BinaryExpression):
    def evaluate(self) -> Any:        
        return self.left.evaluate() * self.right.evaluate() 
    

class AndExpression(BinaryExpression):
    def evaluate(self) -> bool:        
        return self.left.evaluate() and self.right.evaluate() 


class OrExpression(BinaryExpression):
    def evaluate(self) -> bool:        
        return self.left.evaluate() or self.right.evaluate()
    
    
class EqualEqualExpression(BinaryExpression):
    def evaluate(self) -> bool:
        return self.left.evaluate() == self.right.evaluate()


class BangEqualExpression(BinaryExpression):
    def evaluate(self) -> bool:
        return self.left.evaluate() != self.right.evaluate()


class LessExpression(BinaryExpression):
    def evaluate(self) -> bool:
        return self.left.evaluate() < self.right.evaluate()


class LessEqualExpression(BinaryExpression):
    def evaluate(self) -> bool:
        return self.left.evaluate() <= self.right.evaluate()


class GreaterExpression(BinaryExpression):
    def evaluate(self) -> bool:
        return self.left.evaluate() > self.right.evaluate()


class GreaterEqualExpression(BinaryExpression):
    def evaluate(self) -> bool:
        return self.left.evaluate() >= self.right.evaluate()

