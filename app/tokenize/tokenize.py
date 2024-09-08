from argparse import ArgumentParser, Namespace
import sys

from .errors import UnexpectedCharacterError
from .symbols import Symbol, EOFSymbol

def config_tokenize_parser(arg_parser: ArgumentParser) -> None:
    arg_parser.add_argument("file")
    arg_parser.set_defaults(entry=tokenize)


def tokenize(ns: Namespace) -> None:
    with open(ns.file) as fd:
        file_contents = fd.read()
        
    is_error = False

    it = iter(file_contents)
    for char in it:
        if not Symbol.is_symbol(char):
            is_error = True
            print(
                UnexpectedCharacterError(1, char),
                file=sys.stderr
            )
        else:
            print(Symbol.from_chr(char))
        
    print(EOFSymbol())    

    if is_error:
        exit(65)