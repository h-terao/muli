from .parser import parser as default_parser
from .parser import Parser


def exec(parser: Parser = None):
    if parser is None:
        parser = default_parser

    args = parser.parser.parse_args()
    command = args.command(**args.get("__init__", args))
    command.run(args)