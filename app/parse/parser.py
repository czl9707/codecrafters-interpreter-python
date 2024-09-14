from argparse import ArgumentParser, Namespace
from typing import Optional

from ..utils import ParserBaseError
from ..tokens import Tokenizer, EOFSymbol
from ..expressions import Expression


def config_parse_parser(arg_parser: ArgumentParser) -> None:
    arg_parser.add_argument("file")
    arg_parser.set_defaults(entry=print_parse_result)
    
def print_parse_result(ns: Namespace) -> None:
    with open(ns.file) as fd:
        file_contents = fd.read()
    
    tokenizer = Tokenizer(file_contents)
    token_iter = iter(tokenizer)
    expression: Optional[Expression] = None
    
    try:
        for token in token_iter:
            if token.__class__ == EOFSymbol:
                break
            expression = Expression.from_token(token, expression, token_iter)
        print(expression)
    except ParserBaseError as e:
        e.line_num = tokenizer.line
        print(e)
        exit(65)
    