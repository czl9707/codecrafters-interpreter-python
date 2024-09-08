from argparse import ArgumentParser, Namespace

from .errors import UnexpectedCharacterError
from .symbols import Symbol, EOFSymbol

def config_tokenize_parser(arg_parser: ArgumentParser) -> None:
    arg_parser.add_argument("file")
    arg_parser.set_defaults(entry=tokenize)


def tokenize(ns: Namespace) -> None:
    with open(ns.file) as fd:
        file_contents = fd.read()

    tokens = []
    errors = []

    it = iter(file_contents)
    for char in it:
        if not Symbol.is_symbol(char):
            errors.append(
                UnexpectedCharacterError(1, char)
            )
        else:
            tokens.append(Symbol.from_chr(char))
        
    tokens.append(EOFSymbol())    
    
    for e in errors:
        print(e)
    for t in tokens:
        print(t)