from argparse import ArgumentParser, Namespace
import sys
from typing import Optional

from ..utils import ParserBaseError, RuntimeError
from ..tokens import Tokenizer, EOFSymbol
from ..expressions import Expression


def config_parse_parser(arg_parser: ArgumentParser) -> None:
    arg_parser.add_argument("file")
    arg_parser.set_defaults(entry=print_parse_result)
    
    
def config_evaluate_parser(arg_parser: ArgumentParser) -> None:
    arg_parser.add_argument("file")
    arg_parser.set_defaults(entry=print_evalute_result)
    
    
def print_parse_result(ns: Namespace) -> None:
    with open(ns.file) as fd:
        file_contents = fd.read()
    
    parser = Parser(file_contents)
    expr = parser.get_expression()
    if expr:
        print(expr)
    
    if parser.error:
        exit(65)

def print_evalute_result(ns: Namespace) -> None:
    with open(ns.file) as fd:
        file_contents = fd.read()
    
    parser = Parser(file_contents)
    expr = parser.get_expression()
    try:
        if expr:
            value = expr.evaluate()
            if isinstance(value, bool):
                print(str(value).lower())
            elif value is None:
                print("nil")
            else:
                print(value)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        exit(70)
    
    if parser.error:
        exit(65)


class Parser:
    def __init__(self, s:str) -> None:
        self.tokenizer = Tokenizer(s)
        self.self_error = False
    
    @property
    def error(self) -> bool:
        return self.self_error or self.tokenizer.error
    
    def get_expression(self) -> Optional[Expression]:
        token_iter = iter(self.tokenizer)
        expression: Optional[Expression] = None
    
        try:
            for token in token_iter:
                if token.__class__ == EOFSymbol:
                    break
                expression = Expression.from_token(token, expression, token_iter)
            return expression
        except ParserBaseError as e:
            e.line_num = self.tokenizer.line
            print(e, file=sys.stderr)
            self.self_error = True
        
        return None