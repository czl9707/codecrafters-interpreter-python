from argparse import ArgumentParser, Namespace
import sys

from ..parse import Parser
from ..utils import RuntimeError


def config_execute_parser(arg_parser: ArgumentParser) -> None:
    arg_parser.add_argument("file")
    arg_parser.set_defaults(entry=execute_file)
    
    
def execute_file(ns: Namespace) -> None:
    with open(ns.file) as fd:
        file_contents = fd.read()
    
    parser = Parser(file_contents)
    try:
        for expression in parser:
            expression.evaluate()
    except RuntimeError as e:
        print(e, file=sys.stderr)
        exit(70)
    
    if parser.error:
        exit(65)
