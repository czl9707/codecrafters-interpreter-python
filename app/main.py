from argparse import ArgumentParser, Namespace
import sys

from .tokens import Tokenizer
from .parse import Parser
from .execution import ExceutionScope
from .utils import RuntimeError

def main():
    args = parse_args()
    args.entry(args)


def parse_args() -> Namespace:
    arg_parser = ArgumentParser()
    sub_parser = arg_parser.add_subparsers()
    
    arg_parser.add_argument("file")
    config_tokenize_parser(sub_parser.add_parser("tokenize"))
    config_parse_parser(sub_parser.add_parser("parse"))
    config_evaluate_parser(sub_parser.add_parser("evaluate"))
    config_execute_parser(sub_parser.add_parser("run"))
    
    
    return arg_parser.parse_args()




def config_parse_parser(arg_parser: ArgumentParser) -> None:
    arg_parser.set_defaults(entry=print_parse_result)
    
def config_evaluate_parser(arg_parser: ArgumentParser) -> None:
    arg_parser.set_defaults(entry=print_evalute_result)
    
def config_tokenize_parser(arg_parser: ArgumentParser) -> None:
    arg_parser.set_defaults(entry=print_tokens)

def config_execute_parser(arg_parser: ArgumentParser) -> None:
    arg_parser.set_defaults(entry=execute_file)
    
    
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
            value = expression.evaluate(ExceutionScope())
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


def print_tokens(ns: Namespace) -> None:
    with open(ns.file) as fd:
        file_contents = fd.read()
    
    tokenized = Tokenizer(file_contents)
    for token in tokenized:
        print(token)
    
    if tokenized.error:
        exit(65)
    
    
def execute_file(ns: Namespace) -> None:
    with open(ns.file) as fd:
        file_contents = fd.read()
    
    scope = ExceutionScope()
    parser = Parser(file_contents)
    try:
        for expression in parser:
            expression.evaluate(scope)
    except RuntimeError as e:
        print(e, file=sys.stderr)
        exit(70)
    
    if parser.error:
        exit(65)



if __name__ == "__main__":
    main()
