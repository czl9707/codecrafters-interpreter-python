from argparse import ArgumentParser, Namespace

from .symbols import Symbol, EOFSymbol

    

def config_tokenize_parser(arg_parser: ArgumentParser) -> None:
    arg_parser.add_argument("file")
    arg_parser.set_defaults(entry=tokenize)


def tokenize(ns: Namespace) -> None:
    with open(ns.file) as fd:
        file_contents = fd.read()

    it = iter(file_contents)
    for char in it:
        if not Symbol.is_symbol(char):
            raise NotImplementedError()
        
        sym = Symbol.from_chr(char)
    
        print(sym)
    
    print(EOFSymbol())    
    