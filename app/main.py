from argparse import ArgumentParser, Namespace
from .tokens import config_tokenize_parser
from .parse import config_parse_parser, config_evaluate_parser
from .execution import config_execute_parser

def main():
    args = parse_args()
    args.entry(args)


def parse_args() -> Namespace:
    arg_parser = ArgumentParser()
    sub_parser = arg_parser.add_subparsers()
    
    config_tokenize_parser(sub_parser.add_parser("tokenize"))
    config_parse_parser(sub_parser.add_parser("parse"))
    config_evaluate_parser(sub_parser.add_parser("evaluate"))
    config_execute_parser(sub_parser.add_parser("run"))
    
    
    return arg_parser.parse_args()


if __name__ == "__main__":
    main()
