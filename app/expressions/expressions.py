from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Iterator, Optional, Type, Union, cast

from ..utils import MissingExpressionError, NoneNumberOperandError, UnMatchedOprendError

if TYPE_CHECKING:
    from ..tokens import Token


def precedence(pre: int) -> Callable[[Type['Expression']], Type['Expression']]:
    def wrapped(cls: Type['Expression']) -> Type['Expression']:
        cls._precedence = pre
        return cls
    
    return wrapped


@precedence(0)
class Expression(ABC):
    _precedence: int
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
    def yield_from(cls: Type['Expression'], token_cls: Type['Token']):
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
    ) -> "Expression":
        if not prev_expr:
            raise MissingExpressionError(-1, token)
        
        if hasattr(prev_expr, "right"):
            prev_expr = cast(Union['BinaryExpression', 'UnaryExpression'], prev_expr)
            if prev_expr._precedence < cls._precedence:
                _self = cls(token, prev_expr.right, iter)
                prev_expr.right = _self
                return prev_expr
        return cls(token, prev_expr, iter)


class MinusNegativeExpressionRouter(Expression, ABC):
    @staticmethod
    def from_token(
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        iter: Iterator['Token']
    ) -> 'Expression':
        if prev_expr is None:
            return NegativeExpression.from_token(token, None, iter)
        else:
            return MinusExpression.from_token(token, prev_expr, iter)
        

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
@precedence(5)
class NegativeExpression(UnaryExpression):
    def evaluate(self) -> Any:
        right_v = self.right.evaluate()
        if not _is_number(right_v):
            raise NoneNumberOperandError()

        return - right_v


@precedence(5)
class BangExpression(UnaryExpression):
    def evaluate(self) -> bool:        
        return not self.right.evaluate()


class PrintExpression(UnaryExpression):
    def evaluate(self) -> Any:
        value = self.right.evaluate()
        if isinstance(value, bool):
            print(str(value).lower())
        elif value is None:
            print("nil")
        else:
            print(value)

# *********************************************** Binary ***********************************************
@precedence(3)
class PlusExpression(BinaryExpression):
    def evaluate(self) -> Any:        
        left_v = self.left.evaluate()
        right_v = self.right.evaluate()
        if isinstance(left_v, str) and isinstance(right_v, str):
            return left_v + right_v
        if _is_number(left_v) and _is_number(right_v):
            return left_v + right_v
        
        if (
            (_is_string(left_v) or _is_number(left_v)) and
            (_is_string(right_v) or _is_number(right_v))
        ):
            raise UnMatchedOprendError()
        else:
            raise NoneNumberOperandError()
        

@precedence(3)
class MinusExpression(BinaryExpression):
    def evaluate(self) -> Any:
        left_v = self.left.evaluate()
        right_v = self.right.evaluate()
        if not _is_number(left_v) or not _is_number(right_v):
            raise NoneNumberOperandError()
        
        return left_v - right_v
    

@precedence(4)
class DivideExpression(BinaryExpression):
    def evaluate(self) -> Any:
        left_v = self.left.evaluate()
        right_v = self.right.evaluate()
        if not _is_number(left_v) or not _is_number(right_v):
            raise NoneNumberOperandError()
        
        if left_v % right_v:
            return left_v / right_v
        else:
            return left_v // right_v
    
    
@precedence(4)
class MultiplyExpression(BinaryExpression):
    def evaluate(self) -> Any:
        left_v = self.left.evaluate()
        right_v = self.right.evaluate()
        if not _is_number(left_v) or not _is_number(right_v):
            raise NoneNumberOperandError()
        
        return left_v * right_v 
    

class AndExpression(BinaryExpression):
    def evaluate(self) -> bool:        
        return self.left.evaluate() and self.right.evaluate() 


class OrExpression(BinaryExpression):
    def evaluate(self) -> bool:        
        return self.left.evaluate() or self.right.evaluate()
    

@precedence(1)
class EqualEqualExpression(BinaryExpression):
    def evaluate(self) -> bool:
        left_v = self.left.evaluate()
        right_v = self.right.evaluate()
        return left_v == right_v


@precedence(1)
class BangEqualExpression(BinaryExpression):
    def evaluate(self) -> bool:
        left_v = self.left.evaluate()
        right_v = self.right.evaluate()
        return left_v != right_v


@precedence(2)
class LessExpression(BinaryExpression):
    def evaluate(self) -> bool:
        left_v = self.left.evaluate()
        right_v = self.right.evaluate()
        if not _is_number(left_v) or not _is_number(right_v):
            raise NoneNumberOperandError()
        return left_v < right_v

@precedence(2)
class LessEqualExpression(BinaryExpression):
    def evaluate(self) -> bool:
        left_v = self.left.evaluate()
        right_v = self.right.evaluate()
        if not _is_number(left_v) or not _is_number(right_v):
            raise NoneNumberOperandError()
        return left_v <= right_v


@precedence(2)
class GreaterExpression(BinaryExpression):
    def evaluate(self) -> bool:
        left_v = self.left.evaluate()
        right_v = self.right.evaluate()
        if not _is_number(left_v) or not _is_number(right_v):
            raise NoneNumberOperandError()
        return left_v > right_v


@precedence(2)
class GreaterEqualExpression(BinaryExpression):
    def evaluate(self) -> bool:
        left_v = self.left.evaluate()
        right_v = self.right.evaluate()
        if not _is_number(left_v) or not _is_number(right_v):
            raise NoneNumberOperandError()
        return left_v >= right_v



# *********************************************** Util ***********************************************
def _is_number(obj: Any):
    return obj.__class__ == int or obj.__class__ == float

def _is_string(obj: Any):
    return obj.__class__ == str