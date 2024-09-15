from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Iterator, Optional, Type, Union, cast

from ..utils import MissingExpressionError, NoneNumberOperandError, UnMatchedOprendError, RuntimeError

if TYPE_CHECKING:
    from ..tokens import Token
    from ..execution import ExceutionScope, Variable


def precedence(pre: int) -> Callable[[Type['Expression']], Type['Expression']]:
    def wrapped(cls: Type['Expression']) -> Type['Expression']:
        cls._precedence = pre
        return cls
    
    return wrapped


def statement(is_statement: bool = True) -> Callable[[Type['Expression']], Type['Expression']]:
    def wrapped(cls: Type['Expression']) -> Type['Expression']:
        cls._statement = is_statement
        return cls
    
    return wrapped

@precedence(0)
class Expression(ABC):
    _precedence: int
    _statement: bool = False
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
    def evaluate(self, scope: 'ExceutionScope') -> Any:
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

    def evaluate(self, scope: 'ExceutionScope') -> Any:
        if self.expr:
            return self.expr.evaluate(scope)
        else:
            return None


class IdentifierExpression(Expression):
    __slots__ = ["name"]
    name: 'Token'
    
    def __init__(
        self, 
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        iter: Iterator['Token']
    ) -> None:
        self.name = token
    
    @classmethod
    def from_token(
        cls: Type['IdentifierExpression'],
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        iter: Iterator['Token']
    ) -> "IdentifierExpression":
        return cls(token, prev_expr, iter)

    def evaluate(self, scope: 'ExceutionScope') -> Any:
        return scope.fetch_variable(self.name.lexeme).value
    
    def left_value_evaluate(self, scope: 'ExceutionScope') -> 'Variable':
        return scope.fetch_variable(self.name.lexeme)

    def __str__(self) -> str:
        return f"(Identifier {self.name.lexeme})"

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
    ) -> "Expression":
        if prev_expr:        
            right_most = UnaryExpression.__rightest_binary_unary(prev_expr)
            if right_most and right_most.operator == token:
                _self = cls(token, right_most.right, iter)
                right_most.right = _self
                return prev_expr

        return cls(token, prev_expr, iter)

    @staticmethod
    def __rightest_binary_unary(expr: Expression) -> Optional['BinaryExpression']:
        second_rightest: Optional[BinaryExpression] = None
        rightest = expr
        while hasattr(rightest, "right"):
            second_rightest = cast(BinaryExpression, rightest)
            rightest = second_rightest.right
        
        return second_rightest
    

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
        
        right_most = BinaryExpression.__rightest_binary_unary(prev_expr)
        if (
            right_most and (
                (right_most._precedence < cls._precedence) or
                (right_most.operator == token and cls == AssignExpression)
            )
        ):
            _self = cls(token, right_most.right, iter)
            right_most.right = _self
            return prev_expr

        return cls(token, prev_expr, iter)

    @staticmethod
    def __rightest_binary_unary(expr: Expression) -> Optional['BinaryExpression']:
        second_rightest: Optional[BinaryExpression] = None
        rightest = expr
        while hasattr(rightest, "right"):
            second_rightest = cast(BinaryExpression, rightest)
            rightest = second_rightest.right
        
        return second_rightest


class StatementExpression(UnaryExpression):
    ...

# *********************************************** Literal ***********************************************
class StringLiteralExpression(LiteralExpression):
    def __str__(self) -> str:
        return self.value.literal
        
    def evaluate(self, scope: 'ExceutionScope') -> str:
        return self.value.literal
       
        
class NumberLiteralExpression(LiteralExpression):
    def __str__(self) -> str:
        return self.value.literal
        
    def evaluate(self, scope: 'ExceutionScope') -> Union[int, float]:
        if "." in self.value.lexeme:
            return float(self.value.lexeme)
        return int(self.value.lexeme)


class BooleanLiteralExpression(LiteralExpression):
    def __str__(self) -> str:
        return self.value.lexeme

    def evaluate(self, scope: 'ExceutionScope') -> bool:
        return self.value.lexeme == "true"
    

class NilLiteralExpression(LiteralExpression):
    def __str__(self) -> str:
        return self.value.lexeme

    def evaluate(self, scope: 'ExceutionScope') -> None:
        return None

# *********************************************** Unary ***********************************************
@precedence(5)
class NegativeExpression(UnaryExpression):
    def evaluate(self, scope: 'ExceutionScope') -> Any:
        right_v = self.right.evaluate(scope)
        if not _is_number(right_v):
            raise NoneNumberOperandError()

        return - right_v


@precedence(5)
class BangExpression(UnaryExpression):
    def evaluate(self, scope: 'ExceutionScope') -> bool:        
        return not self.right.evaluate(scope)
    
        
# *********************************************** Binary ***********************************************
@precedence(3)
class PlusExpression(BinaryExpression):
    def evaluate(self, scope: 'ExceutionScope') -> Any:        
        left_v = self.left.evaluate(scope)
        right_v = self.right.evaluate(scope)
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
    def evaluate(self, scope: 'ExceutionScope') -> Any:
        left_v = self.left.evaluate(scope)
        right_v = self.right.evaluate(scope)
        if not _is_number(left_v) or not _is_number(right_v):
            raise NoneNumberOperandError()
        
        return left_v - right_v
    

# @precedence(3)
@precedence(4)
class DivideExpression(BinaryExpression):
    def evaluate(self, scope: 'ExceutionScope') -> Any:
        left_v = self.left.evaluate(scope)
        right_v = self.right.evaluate(scope)
        if not _is_number(left_v) or not _is_number(right_v):
            raise NoneNumberOperandError()
        
        if left_v % right_v:
            return left_v / right_v
        else:
            return left_v // right_v
    
    
# @precedence(3)
@precedence(4)
class MultiplyExpression(BinaryExpression):
    def evaluate(self, scope: 'ExceutionScope') -> Any:
        left_v = self.left.evaluate(scope)
        right_v = self.right.evaluate(scope)
        if not _is_number(left_v) or not _is_number(right_v):
            raise NoneNumberOperandError()
        
        return left_v * right_v 
    

class AndExpression(BinaryExpression):
    def evaluate(self, scope: 'ExceutionScope') -> bool:        
        return self.left.evaluate(scope) and self.right.evaluate(scope) 


class OrExpression(BinaryExpression):
    def evaluate(self, scope: 'ExceutionScope') -> bool:        
        return self.left.evaluate(scope) or self.right.evaluate(scope)
    

@precedence(1)
class EqualEqualExpression(BinaryExpression):
    def evaluate(self, scope: 'ExceutionScope') -> bool:
        left_v = self.left.evaluate(scope)
        right_v = self.right.evaluate(scope)
        return left_v == right_v


@precedence(1)
class BangEqualExpression(BinaryExpression):
    def evaluate(self, scope: 'ExceutionScope') -> bool:
        left_v = self.left.evaluate(scope)
        right_v = self.right.evaluate(scope)
        return left_v != right_v


@precedence(2)
class LessExpression(BinaryExpression):
    def evaluate(self, scope: 'ExceutionScope') -> bool:
        left_v = self.left.evaluate(scope)
        right_v = self.right.evaluate(scope)
        if not _is_number(left_v) or not _is_number(right_v):
            raise NoneNumberOperandError()
        return left_v < right_v

@precedence(2)
class LessEqualExpression(BinaryExpression):
    def evaluate(self, scope: 'ExceutionScope') -> bool:
        left_v = self.left.evaluate(scope)
        right_v = self.right.evaluate(scope)
        if not _is_number(left_v) or not _is_number(right_v):
            raise NoneNumberOperandError()
        return left_v <= right_v


@precedence(2)
class GreaterExpression(BinaryExpression):
    def evaluate(self, scope: 'ExceutionScope') -> bool:
        left_v = self.left.evaluate(scope)
        right_v = self.right.evaluate(scope)
        if not _is_number(left_v) or not _is_number(right_v):
            raise NoneNumberOperandError()
        return left_v > right_v


@precedence(2)
class GreaterEqualExpression(BinaryExpression):
    def evaluate(self, scope: 'ExceutionScope') -> bool:
        left_v = self.left.evaluate(scope)
        right_v = self.right.evaluate(scope)
        if not _is_number(left_v) or not _is_number(right_v):
            raise NoneNumberOperandError()
        return left_v >= right_v


class AssignExpression(BinaryExpression):
    def evaluate(self, scope: 'ExceutionScope') -> None:
        assert (
            isinstance(self.left, IdentifierExpression) or 
            isinstance(self.left, VarExpression)
        )
        left_expr = cast(Union[IdentifierExpression, VarExpression], self.left)
        right_v = self.right.evaluate(scope)
        
        var = left_expr.left_value_evaluate(scope)
        var.value = right_v
        
        return right_v


# *********************************************** Statement ***********************************************
@statement()
class PrintExpression(StatementExpression):
    def evaluate(self, scope: 'ExceutionScope') -> Any:
        value = self.right.evaluate(scope)
        if isinstance(value, bool):
            print(str(value).lower())
        elif value is None:
            print("nil")
        else:
            print(value)


@statement()
class VarExpression(StatementExpression):
    def evaluate(self, scope: 'ExceutionScope') -> None:
        r: IdentifierExpression
        if self.right.__class__ == IdentifierExpression:
            r = cast(IdentifierExpression, self.right)
            return scope.create_variable(r.name.lexeme).value
        elif (
            self.right.__class__ == AssignExpression and 
            cast(AssignExpression, self.right).left.__class__ == IdentifierExpression
        ):
            r = cast(IdentifierExpression, cast(AssignExpression, self.right).left)
            scope.create_variable(r.name.lexeme).value
            self.right.evaluate(scope)
            
            return scope.fetch_variable(r.name.lexeme).value
        
        raise RuntimeError()
        
    
    def left_value_evaluate(self, scope: 'ExceutionScope') -> 'Variable':
        self.evaluate(scope)
        r: IdentifierExpression = cast(IdentifierExpression, self.right)
        
        # return variable
        return r.left_value_evaluate(scope)
        

# *********************************************** Util ***********************************************
def _is_number(obj: Any):
    return obj.__class__ == int or obj.__class__ == float

def _is_string(obj: Any):
    return obj.__class__ == str



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