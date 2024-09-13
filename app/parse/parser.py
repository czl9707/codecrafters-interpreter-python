from argparse import ArgumentParser, Namespace
from typing import TYPE_CHECKING, Optional

from ..tokens import Tokenizer, EOFSymbol
from ..expressions import Expression


def config_parse_parser(arg_parser: ArgumentParser) -> None:
    arg_parser.add_argument("file")
    arg_parser.set_defaults(entry=print_parse_result)
    
def print_parse_result(ns: Namespace) -> None:
    with open(ns.file) as fd:
        file_contents = fd.read()
    
    token_iter = iter(Tokenizer(file_contents))
    expression: Optional[Expression] = None
    
    for token in token_iter:
        if token.__class__ == EOFSymbol:
            break
        expression = Expression.from_token(token, expression, token_iter)
    
    print(expression)