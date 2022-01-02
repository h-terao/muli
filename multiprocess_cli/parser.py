from __future__ import annotations
import argparse
import inspect
import functools
import multiprocessing as mp
import types
from pathlib import Path

import docstring_parser
from tqdm import tqdm

from .command import Command


def strtobool(value) -> bool:
    import distutils.util
    return bool(distutils.util.strtobool(value))


class Parser:
    def __init__(self, parser=None, subparsers=None):
        self.parser = argparse.ArgumentParser() if parser is None else parser
        self.subparsers = self.parser.add_subparsers(help="sub-command help") \
            if subparsers is None else subparsers

    def register(self, title: str | None = None, help: str | None = "short"):
        def deco(command: Command):
            self._append_subcommand(command, title, help)
            return command
        return deco

    def run(self):
        args = self.parser.parse_args()
        command = args.command()

        iterable = list(filter(
            functools.partial(command.filter, **args.filter_kwargs(args)),
            command.iterator(**args.iterator_kwargs(args)),
        ))

        process = functools.partial(command.process, **args.process_kwargs(args))

        total = len(iterable)
        workers = args.jobs 
        if workers is None:
            workers = 0
        elif workers < 0:
            workers = max(0, mp.cpu_count() + 1 + workers)

        if workers == 0:
            with tqdm(iterable) as pbar:
                [process(input) for input in pbar]
        else:
            with mp.Pool(workers) as pool, tqdm(total=total) as pbar:
                for _ in pool.imap_unordered(process, iterable):
                    pbar.update(1)

    def shared_args(self, parser):
        parser.add_argument("--jobs", "-j", type=int, default=-1, help="Number of jobs.")
        return parser

    def _append_subcommand(self, command, title, help):
        if title is None:
            title = getattr(command, "name", command.__name__)

        command.process.start_idx = 1
        command.filter.start_idx = 1
        command.iterator.start_idx = 0

        docstring = docstring_parser.parse(inspect.getdoc(command))
        if help == "short":
            help = docstring.short_description
        elif help == "long":
            help = docstring.long_description

        parser = self.subparsers.add_parser(title, help=help)
        parser = self.shared_args(parser)

        for func_name in ("process", "iterator", "filter"):
            func = getattr(command, func_name)
            docstring = docstring_parser.parse(inspect.getdoc(func))

            start_idx = func.start_idx
            if isinstance(inspect.getattr_static(command, func_name), types.FunctionType):
                start_idx += 1 # ignore self.

            sig = inspect.signature(func)
            for key in list(sig.parameters)[start_idx:]:
                args = None 
                help = None 
                for param in docstring.params:
                    _args = list(map(lambda x: x.strip(), param.arg_name.split(",")))
                    if key in map(lambda x: x.strip().replace("-", ""), _args):
                        args = _args 
                        help = param.description
                        break 
                
                if args is None:
                    args = [f"--{key}"]

                arg_type = sig.parameters[key].annotation
                try:
                    arg_type = eval(arg_type)
                except TypeError:
                    pass 

                if arg_type is bool:
                    arg_type = strtobool

                default = sig.parameters[key].default 
                if default is inspect._empty:
                    required = True 
                    default = None 
                else:
                    required = True 

                parser.add_argument(*args, type=arg_type, help=help, default=default, required=required)
        
        def getter(func_name):
            
            func = getattr(command, func_name)
            start_idx = func.start_idx
            if isinstance(inspect.getattr_static(command, func_name), types.FunctionType):
                print(func_name, start_idx)
                start_idx += 1

            def inner(args):
                print(func_name, start_idx, list(inspect.signature(func).parameters)[start_idx:])
                kwargs = {
                    key: getattr(args, key)
                    for key in list(inspect.signature(func).parameters)[start_idx:]
                }
                return kwargs

            return inner 

        parser.set_defaults(
            command=command,
            process_kwargs=getter("process"),
            iterator_kwargs=getter("iterator"),
            filter_kwargs=getter("filter"),
        )


parser = Parser()
