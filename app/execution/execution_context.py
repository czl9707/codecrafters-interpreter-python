from typing import Any, TYPE_CHECKING, cast

from ..utils import UndefinedVariableError

if TYPE_CHECKING:
    from ..expressions import IdentifierExpression

class ExceutionScope:
    _variables: dict[str, 'Variable']
    
    def __init__(self) -> None:
        self._variables = {}
    
    def create_variable(self, name: str) -> 'Variable':
        self._variables[name] = Variable(self, name)
        return self._variables[name]

    def fetch_variable(self, name: str) -> 'Variable':
        if name not in self._variables:
            raise UndefinedVariableError(name)
        return self._variables[name]

class Variable:
    __slots__ = ["scope", "name", "value"]
    value: Any
    def __init__(self, scope: ExceutionScope, name: str) -> None:
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
    