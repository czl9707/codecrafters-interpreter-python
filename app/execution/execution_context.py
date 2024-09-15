from typing import Any, TYPE_CHECKING, Optional, cast

from ..utils import UndefinedVariableError, RuntimeError

if TYPE_CHECKING:
    from ..expressions import IdentifierExpression

class ExecutionContext:
    def __init__(self) -> None:
        self.root_scope = ExecutionScope(None)
        self._current_scope = self.root_scope
    
    @property
    def current_scope(self) -> 'ExecutionScope':
        return self._current_scope
    
    def push_scope(self) -> None:
        self._current_scope = ExecutionScope(self.current_scope)
    
    def pop_scope(self) -> None:
        if not self.current_scope.parent:
            raise RuntimeError()
        
        self._current_scope = self.current_scope.parent


class ExecutionScope:
    _variables: dict[str, 'Variable']
    
    def __init__(self, parent: Optional['ExecutionScope']) -> None:
        self.parent = parent
        self._variables = {}
    
    def create_variable(self, name: str) -> 'Variable':
        self._variables[name] = Variable(self, name)
        return self._variables[name]

    def fetch_variable(self, name: str) -> 'Variable':
        scope: Optional['ExecutionScope'] = self
        while scope:
            if name in self._variables:
                return self._variables[name]
            scope = scope.parent
            
        raise UndefinedVariableError(name)


class Variable:
    __slots__ = ["scope", "name", "value"]
    value: Any
    def __init__(self, scope: ExecutionScope, name: str) -> None:
        self.scope = scope
        self.name = name
        self.value = None
    
    def __hash__(self) -> int:
        return self.name.__hash__()
    
    def __eq__(self, value: object) -> bool:
        if value.__class__ != Variable:
            return False
        else:
            return self.name == cast('Variable', value).name
    