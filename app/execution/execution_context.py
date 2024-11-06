from typing import Any, Optional, cast

from ..utils import UndefinedVariableError, RuntimeError


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
    
    def __init__(self, parent: Optional['ExecutionScope']=None) -> None:
        self.parent = parent
        self._variables = {}
    
    def create_variable(self, name: str) -> 'Variable':
        self._variables[name] = Variable(self, name)
        return self._variables[name]

    def fetch_variable(self, name: str) -> 'Variable':
        scope: Optional['ExecutionScope'] = self
        while scope:
            if name in scope._variables:
                return scope._variables[name]
            scope = scope.parent
            
        raise UndefinedVariableError(name)

    def create_child_scope(self) -> 'ExecutionScope':
        return ExecutionScope(self)


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
    
    def __str__(self) -> str:
        return f"{self.name}: {self.value}"
    
    