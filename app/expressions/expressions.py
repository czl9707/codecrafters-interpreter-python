from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Self, Callable, Iterator, Optional, Type, Union, cast

from app.tokens.tokens import CommaSymbol, ReturnReservedWord
from app.utils.errors import FunctionScopeExpressionError

from ..tokens import (
    AndReservedWord, 
    BangEqualSymbol, 
    BangSymbol, 
    ElseReservedWord, 
    EqualEqualSymbol, 
    EqualSymbol, 
    FalseReservedWord, 
    GreaterEqualSymbol, 
    GreaterSymbol, 
    IfReservedWord, 
    LeftBraceSymbol, 
    RightBraceSymbol,
    LeftParenthesisSymbol, 
    RightParenthesisSymbol,
    LessEqualSymbol, 
    LessSymbol, 
    MinusSymbol, 
    NilReservedWord, 
    NumberLiteral, 
    OrReservedWord, 
    PlusSymbol, 
    PrintReservedWord, 
    SlashSymbol, 
    StarSymbol, 
    StringLiteral, 
    TrueReservedWord, 
    VarReservedWord, 
    WhileReservedWord,
    Identifier,
    ForReservedWord,
    EOFSymbol, 
    SemicolonSymbol,
    FunReservedWord,
)
from ..utils import (
    MissingScopeExpressionError, 
    MissingExpressionError, 
    NoneNumberOperandError, 
    UnMatchedOprendError,
    NotCallableError, 
    RuntimeError,
    ArgumentsNotMatchError,
)

if TYPE_CHECKING:
    from ..tokens import Token
    from ..execution import ExecutionScope, Variable, FunctionScopeBinding


def precedence(pre: int) -> Callable[[Type['Expression']], Type['Expression']]:
    def wrapped(cls: Type['Expression']) -> Type['Expression']:
        cls._precedence = pre
        return cls
    
    return wrapped
    
def right_associative(cls: Type['Expression']) -> Type['Expression']:
    cls._right_associative = True
    return cls


def yield_from(token_cls: Type['Token']) -> Callable[[Type['Expression']], Type['Expression']]:
    def decorator(expr_cls: Type['Expression']) -> Type['Expression']:
        Expression._token2expression_map[token_cls] = expr_cls
        return expr_cls
    
    return decorator


@precedence(0)
class Expression(ABC):
    _precedence: int
    _right_associative: bool = False
    _token2expression_map: dict[Type['Token'], Type['Expression']] = {}
    
    @abstractmethod
    def __init__(
        self, 
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        token_iter: Iterator['Token']
    ) -> None:
        ...
        
    @abstractmethod
    def __str__(self) -> str:
        ...
    
    @staticmethod
    def from_iter(
        token_iter: Iterator['Token'],
        prev_expr: Optional['Expression'],
    ) -> 'Expression':
        token = next(token_iter)
        return Expression.from_token(token, prev_expr, token_iter)
    
    @classmethod
    @abstractmethod
    def from_token(
        cls: Type['Expression'],
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        token_iter: Iterator['Token']
    ) -> 'Expression':
        if token.__class__ not in Expression._token2expression_map:
            raise MissingExpressionError(token)
        
        return Expression._token2expression_map[token.__class__].from_token(token, prev_expr, token_iter)
    
    @abstractmethod
    def evaluate(self, scope: 'ExecutionScope') -> Any:
        ...

class LiteralExpression(Expression, ABC):
    __slots__= ["value"]
    value: 'Token'
    
    def __init__(
        self, 
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        token_iter: Iterator['Token']
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
        token_iter: Iterator['Token']
    ) -> "LiteralExpression":
        return cls(token, prev_expr, token_iter)

class GroupExpression(Expression):
    __slots__ = ["expr"]
    expr: Optional[Expression]
    
    def __init__(
        self, 
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        token_iter: Iterator['Token']
    ) -> None:
        self.expr = None
        for token in token_iter:
            if isinstance(token, RightParenthesisSymbol):
                break
            self.expr = Expression.from_token(token, self.expr, token_iter)
        
    def __str__(self) -> str:
        return f"(group {self.expr if self.expr else ''})"

    @classmethod
    def from_token(
        cls: Type['GroupExpression'],
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        token_iter: Iterator['Token']
    ) -> "GroupExpression":
        return cls(token, prev_expr, token_iter)

    def evaluate(self, scope: 'ExecutionScope') -> Any:
        if self.expr:
            return self.expr.evaluate(scope)
        else:
            return None

@yield_from(Identifier)
class IdentifierExpression(Expression):
    __slots__ = ["name"]
    name: 'Token'
    
    def __init__(
        self, 
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        token_iter: Iterator['Token']
    ) -> None:
        self.name = token
    
    @classmethod
    def from_token(
        cls: Type['IdentifierExpression'],
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        token_iter: Iterator['Token']
    ) -> "IdentifierExpression":
        return cls(token, prev_expr, token_iter)

    def evaluate(self, scope: 'ExecutionScope') -> Any:
        return scope.fetch_variable(self.name.lexeme).value
    
    def left_value_evaluate(self, scope: 'ExecutionScope') -> 'Variable':
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
        token_iter: Iterator['Token']
    ) -> None:
        self.operator = token
        self.right = Expression.from_iter(token_iter, None)

    def __str__(self) -> str:
        return f"({self.operator.lexeme} {self.right})"

    @classmethod
    def from_token(
        cls: Type['UnaryExpression'],
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        token_iter: Iterator['Token']
    ) -> "Expression":
        if prev_expr:        
            right_most = UnaryExpression.__rightest_unary(prev_expr)
            if right_most and right_most.operator == token:
                _self = cls(token, right_most.right, token_iter)
                right_most.right = _self
                return prev_expr

        return cls(token, prev_expr, token_iter)

    @staticmethod
    def __rightest_unary(expr: Expression) -> Optional['UnaryExpression']:
        second_rightest: Optional[Union[UnaryExpression, BinaryExpression]] = None
        rightest = expr
        while hasattr(rightest, "right"):
            second_rightest = cast(Union[UnaryExpression, BinaryExpression], rightest)
            rightest = second_rightest.right
        
        return second_rightest if (second_rightest and isinstance(second_rightest, UnaryExpression)) else None
    

class BinaryExpression(Expression, ABC):
    __slots__ = ["operator", "left", "right"]
    operator: 'Token'
    right: 'Expression'
    left: 'Expression'

    def __init__(
        self, 
        token: 'Token', 
        prev_expr: 'Expression', 
        token_iter: Iterator['Token']
    ) -> None:        
        self.operator = token
        self.left = prev_expr
        self.right = Expression.from_iter(token_iter, None)

    def __str__(self) -> str:
        return f"({self.operator.lexeme} {self.left} {self.right})"

    @classmethod
    def from_token(
        cls: Type['BinaryExpression'],
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        token_iter: Iterator['Token']
    ) -> "Expression":
        if not prev_expr:
            raise MissingExpressionError(token)
        
        return cls.__insert_self_node(token, prev_expr, token_iter)

    @classmethod
    def __insert_self_node(
        cls: Type['BinaryExpression'],
        token: 'Token', 
        current: 'Expression', 
        token_iter: Iterator['Token']
    ) -> "Expression":
        if not hasattr(current, "right") or current._precedence > cls._precedence:
            return cls(token, current, token_iter)

        right_node = cls.__insert_self_node(token, current.right, token_iter)
        if (
            (current.__class__ == right_node.__class__ and current._right_associative) or
            (right_node._precedence > current._precedence)
        ):
            current.right = right_node
            return current    
        else:
            assert isinstance(right_node, BinaryExpression)
            current.right = right_node.left
            right_node.left = current
                        
            return right_node

class StatementExpression(Expression, ABC):
    "StatementExpression's from_token always consume all the way to end of expression" 
    
    @classmethod
    def from_token(
        cls: Type[Self],
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        token_iter: Iterator['Token']
    ) -> Self:
        return cls(token, prev_expr, token_iter)


@yield_from(NilReservedWord)
class NilLiteralExpression(LiteralExpression):
    def __str__(self) -> str:
        return self.value.lexeme

    def evaluate(self, scope: 'ExecutionScope') -> None:
        return None

NIL = NilLiteralExpression(NilReservedWord(), None, iter([]))



def expression_from_iter_till_end(
    token: 'Token',
    token_iter: Iterator['Token'],
    prev_expr: Optional['Expression'] = None,
) -> 'Expression':
    expression = prev_expr
    
    while token:
        if isinstance(token, SemicolonSymbol):
            if expression is prev_expr:
                raise MissingExpressionError(token)
            return cast('Expression', expression)
        
        expression = Expression.from_token(token, expression, token_iter)
        if isinstance(expression, StatementExpression) or isinstance(expression, AST):
            return expression
        token = next(token_iter)

    raise MissingExpressionError(token)


def expression_from_iter_till(
    token_iter: Iterator['Token'],
    endTokenTypes: list[Type['Token']],
    *,
    allow_nil: bool  = False
) -> 'Expression':
    exp: Optional['Expression'] = None

    for token in token_iter:
        if any(isinstance(token, T) for T in endTokenTypes):
            break
        exp = Expression.from_token(token, exp, token_iter)
        if isinstance(exp, StatementExpression) and (SemicolonSymbol in endTokenTypes):
            return exp
    
    if exp is None: 
        if allow_nil:
            return NIL
        raise MissingExpressionError(token)
    return exp



# *********************************************** Literal ***********************************************
@yield_from(StringLiteral)
class StringLiteralExpression(LiteralExpression):
    def __str__(self) -> str:
        return self.value.literal
        
    def evaluate(self, scope: 'ExecutionScope') -> str:
        return self.value.literal
       
@yield_from(NumberLiteral)
class NumberLiteralExpression(LiteralExpression):
    def __str__(self) -> str:
        return self.value.literal
        
    def evaluate(self, scope: 'ExecutionScope') -> Union[int, float]:
        if "." in self.value.lexeme:
            return float(self.value.lexeme)
        return int(self.value.lexeme)

@yield_from(FalseReservedWord)
@yield_from(TrueReservedWord)
class BooleanLiteralExpression(LiteralExpression):
    def __str__(self) -> str:
        return self.value.lexeme

    def evaluate(self, scope: 'ExecutionScope') -> bool:
        return self.value.lexeme == "true"


# *********************************************** Unary ***********************************************
@precedence(5)
class NegativeExpression(UnaryExpression):
    def evaluate(self, scope: 'ExecutionScope') -> Any:
        right_v = self.right.evaluate(scope)
        if not _is_number(right_v):
            raise NoneNumberOperandError()

        return - right_v


@yield_from(BangSymbol)
@precedence(5)
class BangExpression(UnaryExpression):
    def evaluate(self, scope: 'ExecutionScope') -> bool:        
        return not self.right.evaluate(scope)
    
        
# *********************************************** Binary ***********************************************
@yield_from(PlusSymbol)
@precedence(3)
class PlusExpression(BinaryExpression):
    def evaluate(self, scope: 'ExecutionScope') -> Any:        
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
    def evaluate(self, scope: 'ExecutionScope') -> Any:
        left_v = self.left.evaluate(scope)
        right_v = self.right.evaluate(scope)
        if not _is_number(left_v) or not _is_number(right_v):
            raise NoneNumberOperandError()
        
        return left_v - right_v
    

# @precedence(3)
@yield_from(SlashSymbol)
@precedence(4)
class DivideExpression(BinaryExpression):
    def evaluate(self, scope: 'ExecutionScope') -> Any:
        left_v = self.left.evaluate(scope)
        right_v = self.right.evaluate(scope)
        if not _is_number(left_v) or not _is_number(right_v):
            raise NoneNumberOperandError()
        
        if left_v % right_v:
            return left_v / right_v
        else:
            return left_v // right_v
    
    
# @precedence(3)
@yield_from(StarSymbol)
@precedence(4)
class MultiplyExpression(BinaryExpression):
    def evaluate(self, scope: 'ExecutionScope') -> Any:
        left_v = self.left.evaluate(scope)
        right_v = self.right.evaluate(scope)
        if not _is_number(left_v) or not _is_number(right_v):
            raise NoneNumberOperandError()
        
        return left_v * right_v 
    
@yield_from(AndReservedWord)
class AndExpression(BinaryExpression):
    def evaluate(self, scope: 'ExecutionScope') -> bool:   
        left_result = self.left.evaluate(scope)
        if not _is_truthy(left_result):
            return False
              
        return self.right.evaluate(scope) 

@yield_from(OrReservedWord)
class OrExpression(BinaryExpression):
    def evaluate(self, scope: 'ExecutionScope') -> bool:
        left_result = self.left.evaluate(scope)
        if _is_truthy(left_result):
            return left_result
        return self.right.evaluate(scope)
    

@yield_from(EqualEqualSymbol)
@precedence(1)
class EqualEqualExpression(BinaryExpression):
    def evaluate(self, scope: 'ExecutionScope') -> bool:
        left_v = self.left.evaluate(scope)
        right_v = self.right.evaluate(scope)
        return left_v == right_v


@yield_from(BangEqualSymbol)
@precedence(1)
class BangEqualExpression(BinaryExpression):
    def evaluate(self, scope: 'ExecutionScope') -> bool:
        left_v = self.left.evaluate(scope)
        right_v = self.right.evaluate(scope)
        return left_v != right_v


@yield_from(LessSymbol)
@precedence(2)
class LessExpression(BinaryExpression):
    def evaluate(self, scope: 'ExecutionScope') -> bool:
        left_v = self.left.evaluate(scope)
        right_v = self.right.evaluate(scope)
        if not _is_number(left_v) or not _is_number(right_v):
            raise NoneNumberOperandError()
        return left_v < right_v


@yield_from(LessEqualSymbol)
@precedence(2)
class LessEqualExpression(BinaryExpression):
    def evaluate(self, scope: 'ExecutionScope') -> bool:
        left_v = self.left.evaluate(scope)
        right_v = self.right.evaluate(scope)
        if not _is_number(left_v) or not _is_number(right_v):
            raise NoneNumberOperandError()
        return left_v <= right_v


@yield_from(GreaterSymbol)
@precedence(2)
class GreaterExpression(BinaryExpression):
    def evaluate(self, scope: 'ExecutionScope') -> bool:
        left_v = self.left.evaluate(scope)
        right_v = self.right.evaluate(scope)
        if not _is_number(left_v) or not _is_number(right_v):
            raise NoneNumberOperandError()
        return left_v > right_v


@yield_from(GreaterEqualSymbol)
@precedence(2)
class GreaterEqualExpression(BinaryExpression):
    def evaluate(self, scope: 'ExecutionScope') -> bool:
        left_v = self.left.evaluate(scope)
        right_v = self.right.evaluate(scope)
        if not _is_number(left_v) or not _is_number(right_v):
            raise NoneNumberOperandError()
        return left_v >= right_v


@yield_from(EqualSymbol)
@right_associative
class AssignExpression(BinaryExpression):
    def evaluate(self, scope: 'ExecutionScope') -> None:
        assert (
            isinstance(self.left, IdentifierExpression) or 
            isinstance(self.left, VarExpression)
        )
        left_expr = cast(Union[IdentifierExpression, VarExpression], self.left)
        right_v = self.right.evaluate(scope)
        
        var = left_expr.left_value_evaluate(scope)
        var.set_value(right_v)
        
        return right_v


# *********************************************** Statement ***********************************************
@yield_from(PrintReservedWord)
class PrintExpression(StatementExpression):
    __slots__= ["body"]
    body: Expression
    
    def __init__(
        self, 
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        token_iter: Iterator['Token']
    ) -> None:
        assert isinstance(token, PrintReservedWord)
        
        self.body = expression_from_iter_till_end(next(token_iter), token_iter)
    
    def __str__(self) -> str:
        return f"(print {self.body})"
    
    def evaluate(self, scope: 'ExecutionScope') -> Any:
        value = self.body.evaluate(scope)
        if isinstance(value, bool):
            print(str(value).lower())
        elif value is None:
            print("nil")
        else:
            print(value)


@yield_from(VarReservedWord)
class VarExpression(StatementExpression):
    __slots__ = ["identifier", "assignment"]
    identifier: IdentifierExpression
    assignment: Optional[AssignExpression]
    
    def __init__(
        self, 
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        token_iter: Iterator['Token']
    ) -> None:
        self.assignment = None
        assert isinstance(token, VarReservedWord)
        
        expr = expression_from_iter_till_end(next(token_iter), token_iter)
        if isinstance(expr, AssignExpression):
            self.assignment = cast(AssignExpression, expr)
            assert self.assignment.left.__class__ == IdentifierExpression
            self.identifier = cast(IdentifierExpression, self.assignment.left)
        elif expr.__class__ == IdentifierExpression:
            self.identifier = cast(IdentifierExpression, expr)
        else:
            raise RuntimeError()
    
    def __str__(self) -> str:
        return f"(var {self.assignment if self.assignment else self.identifier})"
    
    def evaluate(self, scope: 'ExecutionScope') -> Any:
        value = None
        if self.assignment:
            value = self.assignment.right.evaluate(scope)
        variable = scope.create_variable(self.identifier.name.lexeme)
        variable.set_value(value)
        
        return variable.value
    
    def left_value_evaluate(self, scope: 'ExecutionScope') -> 'Variable':
        self.evaluate(scope)
        return self.identifier.left_value_evaluate(scope)


@yield_from(IfReservedWord)
class IfExpression(StatementExpression):
    __slots__ = ["predicates", "expression"]
    predicates: Expression
    expression: Expression
    
    def __init__(
        self, 
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        token_iter: Iterator['Token']
    ) -> None:
        assert isinstance(token, IfReservedWord)
        
        token = next(token_iter)
        assert isinstance(token, LeftParenthesisSymbol)
        self.predicates = Expression.from_token(token, None, token_iter)
        token = next(token_iter)
        if isinstance(token, VarReservedWord):
            raise MissingExpressionError(token)
        self.expression = expression_from_iter_till_end(token, token_iter)
        

    def __str__(self) -> str:
        return f"if {self.predicates} \n {self.expression}"
    
    def evaluate(self, scope: 'ExecutionScope') -> Any:
        scope.if_statement_predicate = _is_truthy(self.predicates.evaluate(scope))
        if scope.if_statement_predicate:
            self.expression.evaluate(scope)


@yield_from(ElseReservedWord)
class ElseExpression(StatementExpression):
    __slots__ = ["expression"]
    expression: Expression

    def __init__(
        self, 
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        token_iter: Iterator['Token']
    ) -> None:
        # assert (
        #     isinstance(prev_expr, IfExpression) or (
        #         isinstance(prev_expr, ElseExpression) and
        #         isinstance(prev_expr.expression, IfExpression)
        #     )
        # )
        assert isinstance(token, ElseReservedWord)    
        
        token = next(token_iter)
        if isinstance(token, VarReservedWord):
            raise MissingExpressionError(token)
        self.expression = expression_from_iter_till_end(token, token_iter)

    def __str__(self) -> str:
        return f"else\n{self.expression}"
    
    def evaluate(self, scope: 'ExecutionScope') -> Any:
        if not scope.if_statement_predicate:
            self.expression.evaluate(scope)


@yield_from(WhileReservedWord)
class WhileExpression(StatementExpression):
    __slots__ = ["predicates", "expression"]
    predicates: Expression
    expression: Expression
    
    def __init__(
        self, 
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        token_iter: Iterator['Token']
    ) -> None:
        assert isinstance(token, WhileReservedWord)
        
        token = next(token_iter)
        assert isinstance(token, LeftParenthesisSymbol)
        self.predicates = Expression.from_token(token, None, token_iter)
        
        token = next(token_iter)
        if isinstance(token, VarReservedWord):
            raise MissingExpressionError(token)
        self.expression = expression_from_iter_till_end(token, token_iter)


    def __str__(self) -> str:
        return f"while {self.predicates} \n {self.expression}"
    
    def evaluate(self, scope: 'ExecutionScope') -> Any:
        while _is_truthy(self.predicates.evaluate(scope)):
            if scope.function_return_value[0]:
                break
            self.expression.evaluate(scope)
            

@yield_from(ForReservedWord)
class ForExpression(StatementExpression):
    __slots__ = ["initialization", "predicates", "step", "expression"]
    initialization: Expression
    step: Expression
    predicates: Expression
    expression: Expression
    
    def __init__(
        self, 
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        token_iter: Iterator['Token']
    ) -> None:
        assert isinstance(token, ForReservedWord)
        
        token = next(token_iter)
        assert isinstance(token, LeftParenthesisSymbol)

        self.initialization = expression_from_iter_till(token_iter, [SemicolonSymbol], allow_nil=True)
        if isinstance(self.initialization, AST):
            raise MissingExpressionError(token)
        
        self.predicates = expression_from_iter_till(token_iter, [SemicolonSymbol], allow_nil=True)
        if isinstance(self.predicates, AST):
            raise MissingExpressionError(token)
        
        self.step = expression_from_iter_till(token_iter, [RightParenthesisSymbol], allow_nil=True)
        if isinstance(self.step, AST):
            raise MissingExpressionError(token)
        
        token = next(token_iter)
        if isinstance(token, VarReservedWord):
            raise MissingExpressionError(token)
        self.expression = expression_from_iter_till_end(token, token_iter)

    def __str__(self) -> str:
        return f"for ({self.initialization};{self.predicates};{self.step}) \n {self.expression}"
    
    def evaluate(self, scope: 'ExecutionScope') -> Any:
        self.initialization.evaluate(scope)
        while True:
            if not _is_truthy(self.predicates.evaluate(scope)):
                break
            if scope.function_return_value[0]:
                break
            
            self.expression.evaluate(scope)
            self.step.evaluate(scope)
            


@yield_from(FunReservedWord)
class FunctionDefinitionExpression(StatementExpression):
    __slots__ = ["name", "parameters", "body"]
    name: str
    parameters: list[str]
    body: Expression
    
    def __init__(
        self, 
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        token_iter: Iterator['Token']
    ) -> None:
        assert isinstance(token, FunReservedWord)
        token = next(token_iter)
        assert isinstance(token, Identifier)
        self.name = token.lexeme
        
        token = next(token_iter)
        assert isinstance(token, LeftParenthesisSymbol)
        self.parameters = []
        
        for token in token_iter:
            if isinstance(token, RightParenthesisSymbol):
                break
            
            assert isinstance(token, Identifier)
            self.parameters.append(token.lexeme)
            token = next(token_iter)

            if isinstance(token, RightParenthesisSymbol):
                break
            elif isinstance(token, CommaSymbol):
                continue
            else:
                raise MissingExpressionError(token)
        
        token = next(token_iter)
        if not isinstance(token, LeftBraceSymbol):
            raise FunctionScopeExpressionError(token)
        self.body = expression_from_iter_till_end(token, token_iter)

    def __str__(self) -> str:
        return f"<fn {self.name}>"
    
    def evaluate(self, scope: 'ExecutionScope') -> Any:
        var = scope.create_variable(self.name)
        var.set_function_value(self, scope.create_child_scope())


@yield_from(ReturnReservedWord)
class ReturnExpression(StatementExpression):
    __slots__= ["body"]
    body: Expression
    
    def __init__(
        self, 
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        token_iter: Iterator['Token']
    ) -> None:
        assert isinstance(token, ReturnReservedWord)
        
        self.body = expression_from_iter_till(token_iter, [SemicolonSymbol], allow_nil=True)
    
    def __str__(self) -> str:
        return f"(return {self.body})"
    
    def evaluate(self, scope: 'ExecutionScope') -> Any:
        value = self.body.evaluate(scope)
        scope.function_return_value = (True, value)

    
# *********************************************** AST ***********************************************

# AST token will generate a this guy
@yield_from(LeftBraceSymbol)
class AST(Expression):
    __slots__=["children"]
    children: list[Expression]
    
    def __init__(
        self, 
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        token_iter: Iterator['Token']
    ) -> None:
        self.children = []
        
        assert isinstance(token, LeftBraceSymbol)
        token = next(token_iter)
        while token:
            if isinstance(token, RightBraceSymbol):
                return
            
            expression = expression_from_iter_till_end(token, token_iter)
            self.children.append(expression)
            token = next(token_iter)
        
        raise MissingScopeExpressionError()

    @classmethod
    def from_token(
        cls: Type[Self],
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        token_iter: Iterator['Token']
    ) -> Self:
        return cls(token, prev_expr, token_iter)
                
    def __str__(self) -> str:
        return "\n".join([str(exp) for exp in self.children])
    
    def evaluate(self, scope: 'ExecutionScope') -> None:
        local_scope = scope.create_child_scope()
        for child in self.children:
            child.evaluate(local_scope)
            if local_scope.function_return_value[0]:
                scope.function_return_value = local_scope.function_return_value
                return
                


# passing in dummy token to avoid { as the first token
class RootAST(AST):
    __slots__=["children"]
    children: list[Expression]
    
    def __init__(
        self, 
        token: 'Token', # dummy token
        prev_expr: Optional['Expression'], 
        token_iter: Iterator['Token']
    ) -> None:
        self.children = []
        
        token = next(token_iter)
        while token:
            if isinstance(token, EOFSymbol):
                return
            
            expression = expression_from_iter_till_end(token, token_iter)
            self.children.append(expression)
            token = next(token_iter)
        
        raise MissingScopeExpressionError()


# *********************************************** Call ***********************************************
class FunctionCallExpression(Expression):
    __slots__ = ["identifier", "call_parameters"]
    identifier: Optional['Expression']
    call_parameters : list[Expression]
    
    def __init__(
        self, 
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        token_iter: Iterator['Token']
    ) -> None:
        assert isinstance(token, LeftParenthesisSymbol)
        
        self.identifier = prev_expr
        self.call_parameters = []
        
        param: Optional[Expression] = None 
        for token in token_iter:
            if not self.call_parameters and isinstance(token, RightParenthesisSymbol) and not param:
                break
            if isinstance(token, CommaSymbol) or isinstance(token, RightParenthesisSymbol):
                if param is None:
                    raise MissingExpressionError(token)
                self.call_parameters.append(param)
                param = None

                if isinstance(token, CommaSymbol):
                    continue
                else:
                    break
            
            param = Expression.from_token(token, param, token_iter)
            
    @classmethod
    def from_token(
        cls: Type[Self],
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        token_iter: Iterator['Token']
    ) -> Self:
        return cls(token, prev_expr, token_iter)
                
    def __str__(self) -> str:
        return f"{self.identifier} ({','.join(str(p) for p in self.call_parameters)})"
    
    def evaluate(self, scope: 'ExecutionScope') -> None:
        v:'FunctionScopeBinding' = self.identifier.evaluate(scope)  # type: ignore
        if v.__class__.__name__ != 'FunctionScopeBinding':
            raise NotCallableError()
        funcdef, closure = v.funcdef, v.closure
        
        if len(funcdef.parameters) != len(self.call_parameters):
            raise ArgumentsNotMatchError(len(funcdef.parameters), len(self.call_parameters))
        
        func_scope = closure.clone()
        for i in range(len(funcdef.parameters)):
            var = func_scope.create_variable(funcdef.parameters[i])
            var.set_value(self.call_parameters[i].evaluate(scope))
        
        funcdef.body.evaluate(func_scope)
        return func_scope.function_return_value[1]


# *********************************************** Util ***********************************************

def _is_number(obj: Any):
    return obj.__class__ == int or obj.__class__ == float

def _is_string(obj: Any):
    return obj.__class__ == str

def _is_truthy(value: Any):
    if value is None or value is False:
        return False
    return True

@yield_from(MinusSymbol)
class MinusNegativeExpressionRouter(Expression, ABC):
    @staticmethod
    def from_token(
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        token_iter: Iterator['Token']
    ) -> 'Expression':
        if prev_expr is None:
            return NegativeExpression.from_token(token, None, token_iter)
        else:
            return MinusExpression.from_token(token, prev_expr, token_iter)
        
@yield_from(LeftParenthesisSymbol)
class GroupFunctionCallExpressionRouter(Expression, ABC):
    @staticmethod
    def from_token(
        token: 'Token', 
        prev_expr: Optional['Expression'], 
        token_iter: Iterator['Token']
    ) -> 'Expression':
        current_expr = prev_expr
        parent_expr = None
        while isinstance(current_expr, BinaryExpression) or isinstance(current_expr, UnaryExpression):
            parent_expr = current_expr
            current_expr = current_expr.right
        
        if (
            isinstance(current_expr, IdentifierExpression) or 
            isinstance(current_expr, FunctionCallExpression) or
            (isinstance(current_expr, LiteralExpression) and not isinstance(current_expr, NilLiteralExpression))or
            isinstance(current_expr, GroupExpression)
        ):
            if parent_expr:
                parent_expr.right = FunctionCallExpression.from_token(token, current_expr, token_iter)
                return prev_expr # type: ignore
            return FunctionCallExpression.from_token(token, prev_expr, token_iter)
        else:
            return GroupExpression.from_token(token, prev_expr, token_iter)