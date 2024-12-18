from datetime import datetime
from typing import Any, Optional, Union, cast
from xmlrpc.client import boolean

from ..expressions import FunctionDefinitionExpression, define_built_in_function
from ..utils import UndefinedVariableError, RuntimeError



class ExecutionContext:
    def __init__(self) -> None:
        self.root_scope = ExecutionScope()
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
    if_statement_predicate = False
    function_return_value: tuple[bool, Any] = (False, None)  # bool means returned or not, Any is return value
    
    def __init__(self, parent: Optional['ExecutionScope']=None) -> None:
        self.parent = parent
        self._variables = {}
        
        if self.parent is None:
            self._variables["clock"] = Variable(self, "clock")
            self._variables["clock"]._value = FunctionScopeBinding(
                define_built_in_function(
                    "clock", 
                    [], 
                    lambda: int(datetime.now().timestamp()), 
                    self
                ),
                self)
    
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
    
    def clone(self) -> 'ExecutionScope':
        closure = ExecutionScope(self.parent)
        closure._variables = {**self._variables}
        return closure 

    def __str__(self) -> str:
        lines = []
        lines.append("scope: " + super().__str__())
        lines.append("variables:" + ",".join(f"{key}:{value.value}" for key, value in self._variables.items()))
        lines.append("parent:" + str(self.parent).replace('\n', '\n  '))        
        return "\n".join(lines)

class Variable:
    __slots__ = ["scope", "name", "_value"]
    _value: Union[int, float, str, None, bool, 'FunctionScopeBinding']
    def __init__(self, scope: ExecutionScope, name: str) -> None:
        self.scope = scope
        self.name = name
        self._value = None
    
    @property
    def value(self) -> Union[int, float, str, None, bool, 'FunctionScopeBinding']:
        return self._value
    
    def set_value(self, value: Union[int, float, str, None, bool]) -> None :
        self._value = value
    
    def set_function_value(self, funcdef: 'FunctionDefinitionExpression', closure: ExecutionScope):
        self._value = FunctionScopeBinding(funcdef, closure)
    
    def is_function(self) -> boolean:
        return isinstance(self._value, FunctionScopeBinding)
    
    def __hash__(self) -> int:
        return self.name.__hash__()
    
    def __eq__(self, value: object) -> bool:
        if value.__class__ != Variable:
            return False
        else:
            return self.name == cast('Variable', value).name
    
    def __str__(self) -> str:
        return f"{self.name}: {self.value}"
    

class FunctionScopeBinding:
    __slots__ = ["funcdef", "closure"]
    def __init__(self, funcdef: 'FunctionDefinitionExpression', closure: ExecutionScope) -> None:
        self.funcdef = funcdef
        self.closure = closure
    
    def __str__(self) -> str:
        return str(self.funcdef)
    
    