from argparse import ArgumentParser, Namespace
from typing import TYPE_CHECKING

from ..tokens import Tokenizer

if TYPE_CHECKING:
    from ..expressions.expressions import Expression

def config_parse_parser(arg_parser: ArgumentParser) -> None:
    arg_parser.add_argument("file")
    arg_parser.set_defaults(entry=print_parse_result)
    
def print_parse_result(ns: Namespace) -> None:
    with open(ns.file) as fd:
        file_contents = fd.read()
    
    token_iter = iter(Tokenizer(file_contents))
    expressions: list[Expression] = []
    root: Expression = next(token_iter).as_expression()
    leaf: Expression = root
    
    for token in token_iter:
        pass
    
    print(root)