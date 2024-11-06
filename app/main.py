from argparse import ArgumentParser, Namespace
import sys


from .expressions import Expression
from .tokens import Tokenizer, EOFSymbol
from .parse import Parser
from .execution import ExecutionScope
from .utils import RuntimeError, ParserBaseError

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
    
    try:
        tokenizer = Tokenizer(file_contents)
        token_iter = iter(tokenizer)
        expression = None
        for token in token_iter:
            if isinstance(token, EOFSymbol):
                break
            expression = Expression.from_token(token, expression, token_iter)
        
        print(expression)
    except ParserBaseError as e:
        print(f"[line 1] {e}", file=sys.stderr)
        exit(65)

    if tokenizer.error:
        exit(65)

def print_evalute_result(ns: Namespace) -> None:
    with open(ns.file) as fd:
        file_contents = fd.read()
    
    try:
        token_iter = iter(Tokenizer(file_contents))
        scope = ExecutionScope()
        expression = None
        for token in token_iter:
            if isinstance(token, EOFSymbol):
                break
            expression = Expression.from_token(token, expression, token_iter)
        if expression:
            result = expression.evaluate(scope)
            
            if isinstance(result, bool):
                print(str(result).lower())
            elif result is None:
                print("nil")
            else:
                print(result)

    except RuntimeError as e:
        print(e, file=sys.stderr)
        exit(70)
    except ParserBaseError as e:
        print(f"[line 1] {e}", file=sys.stderr)
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
    
    parser = Parser(file_contents)
    if parser.error:
        exit(65)
    
    try:
        parser.ast.evaluate(ExecutionScope())
    except RuntimeError as e:
        print(e, file=sys.stderr)
        exit(70)



if __name__ == "__main__":
    main()
