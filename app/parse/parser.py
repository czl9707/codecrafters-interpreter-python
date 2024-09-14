from argparse import ArgumentParser, Namespace
import sys
from typing import Iterator, Optional

from ..utils import ParserBaseError, RuntimeError
from ..tokens import Tokenizer, EOFSymbol, SemicolonSymbol
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
    for expression in parser:
        print(expression)
    
    if parser.error:
        exit(65)

def print_evalute_result(ns: Namespace) -> None:
    with open(ns.file) as fd:
        file_contents = fd.read()
    
    parser = Parser(file_contents)
    try:
        for expression in parser:
            value = expression.evaluate()
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
    
    def __iter__(self) -> Iterator[Expression]:
        token_iter = iter(self.tokenizer)
        expression: Optional[Expression] = None
    
        try:
            for token in token_iter:
                if token.__class__ == EOFSymbol:
                    break
                if token.__class__ == SemicolonSymbol:
                    if expression:
                        yield expression
                    expression = None
                    continue
                
                expression = Expression.from_token(token, expression, token_iter)
            
            if expression:
                yield expression
        except ParserBaseError as e:
            e.line_num = self.tokenizer.line
            print(e, file=sys.stderr)
            self.self_error = True