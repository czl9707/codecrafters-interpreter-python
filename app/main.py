from argparse import ArgumentParser, Namespace
from .tokens import config_tokenize_parser
from .parse import config_parse_parser

def main():
    args = parse_args()
    args.entry(args)


def parse_args() -> Namespace:
    arg_parser = ArgumentParser()
    sub_parser = arg_parser.add_subparsers()
    
    config_tokenize_parser(sub_parser.add_parser("tokenize"))
    config_parse_parser(sub_parser.add_parser("parse"))

    
    return arg_parser.parse_args()


if __name__ == "__main__":
    main()
