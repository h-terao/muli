from __future__ import annotations
import argparse
import inspect
import types
import warnings
from pathlib import Path  # required.

import docstring_parser
from .command import Command


def strtobool(value) -> bool:
    import distutils.util
    return bool(distutils.util.strtobool(value))


class Parser:
    def __init__(self, parser=None, subparsers=None):
        self.parser = argparse.ArgumentParser() if parser is None else parser
        self.subparsers = self.parser.add_subparsers(help="sub-command help", required=True) \
            if subparsers is None else subparsers

    def register(self, title: str | None = None, help: str | None = "short"):
        def deco(command: Command):
            self._append_subcommand(command, title, help)
            return command
        return deco

    def _append_subcommand(self, command, title, help):
        if title is None:
            title = getattr(command, "name", command.__name__)

        # name: start index
        functions = {
            "__init__": 0,
            "preprocess": 0,
            "glob": 0,
            "filter": 1,
            "step": 1,
            "after_step": 1,
            "postprocess": 1,
        }

        docstring = docstring_parser.parse(inspect.getdoc(command))
        if help == "short":
            help = docstring.short_description
        elif help == "long":
            help = docstring.long_description

        parser = self.subparsers.add_parser(title, help=help)

        arguments = {}
        for name, start_idx in functions.items():
            func = getattr(command, name)

            docstring = docstring_parser.parse(inspect.getdoc(func))
            if isinstance(inspect.getattr_static(command, name), types.FunctionType):
                start_idx += 1 # ignore self.

            sig = inspect.signature(func)
            for key in list(sig.parameters)[start_idx:]:
                if key in arguments:
                    argument = arguments[key]
                else:
                    argument = {
                        "args": set(),
                        "type": None,
                        "help": None,
                        "default": None,
                        "raise_help_warning": False,
                    }

                args = None
                help = None
                for param in docstring.params:
                    _args = list(map(lambda x: x.strip(), param.arg_name.split(",")))
                    if key in map(lambda x: x.strip().replace("-", ""), _args):
                        args = _args
                        help = param.description
                        break

                # Update args.
                if args is None:
                    args = [f"--{key}"]
                argument["args"] |= set(args)

                # Update help.
                if help is not None:
                    if argument["help"] is None:
                        argument["help"] = help
                    elif argument["help"] != help and not argument["raise_help_warning"]:
                        help = argument["help"]
                        warnings.warn((
                            f"{key} is used multiple times, but help messages are different. "
                            f"As help message of {key}, `{help}` is used."
                        ))
                        argument["raise_help_warning"] = True

                # Update type.
                arg_type = sig.parameters[key].annotation
                try:
                    arg_type = eval(arg_type)
                except TypeError:
                    pass
                if arg_type is bool:
                    arg_type = strtobool

                if argument["type"] is None:
                    argument["type"] = arg_type
                elif argument["type"] is not arg_type:
                    raise ValueError((
                        f"{key} is used multiple times, but annotated as different types. "
                        f"You must annotate all {key} as the same type."
                    ))

                # Update default value.
                default = sig.parameters[key].default
                if default is not inspect._empty:
                    if argument["default"] is None:
                        argument["default"] = default
                    elif argument["default"] != default:
                        raise ValueError((
                            f"{key} is used multiple times, but default values are different. "
                            f"You must set all default values of {key} as the same value."
                        ))

                arguments[key] = argument

        for key, argument in arguments.items():
            required = argument["default"] is None
            parser.add_argument(
                *argument["args"],
                type=argument["type"],
                default=argument["default"],
                required=required,
                help=argument["help"],
            )

        def get(name, args):
            f = getattr(command, name)
            start_idx = functions[name]
            if isinstance(inspect.getattr_static(command, name), types.FunctionType):
                start_idx += 1
            return {
                key: getattr(args, key)
                for key in list(inspect.signature(f).parameters)[start_idx:]
            }

        parser.set_defaults(
            command=command,
            get=get,
        )

        # def getter(func_name):

        #     func = getattr(command, func_name)
        #     start_idx = func.start_idx
        #     if isinstance(inspect.getattr_static(command, func_name), types.FunctionType):
        #         start_idx += 1

        #     def inner(args):
        #         kwargs = {
        #             key: getattr(args, key)
        #             for key in list(inspect.signature(func).parameters)[start_idx:]
        #         }
        #         return kwargs

        #     return inner

        # parser.set_defaults(
        #     command=command,
        #     process_kwargs=getter("process"),
        #     glob_kwargs=getter("glob"),
        #     filter_kwargs=getter("filter"),
        #     init_kwargs=getter("initialize"),
        # )

        # for func_name in ("process", "glob", "filter", "initialize"):
        #     func = getattr(command, func_name)
        #     docstring = docstring_parser.parse(inspect.getdoc(func))

        #     start_idx = func.start_idx
        #     sig = inspect.signature(func)
        #     for key in list(sig.parameters)[start_idx:]:
        #         args = None
        #         help = None
        #         for param in docstring.params:
        #             _args = list(map(lambda x: x.strip(), param.arg_name.split(",")))
        #             if key in map(lambda x: x.strip().replace("-", ""), _args):
        #                 args = _args
        #                 help = param.description
        #                 break

        #         if args is None:
        #             args = [f"--{key}"]

        #         arg_type = sig.parameters[key].annotation
        #         try:
        #             arg_type = eval(arg_type)
        #         except TypeError:
        #             pass

        #         if arg_type is bool:
        #             arg_type = strtobool

        #         default = sig.parameters[key].default
        #         if default is inspect._empty:
        #             required = True
        #             default = None
        #         else:
        #             required = True

        #         parser.add_argument(*args, type=arg_type, help=help, default=default, required=required)

        # def getter(func_name):

        #     func = getattr(command, func_name)
        #     start_idx = func.start_idx
        #     if isinstance(inspect.getattr_static(command, func_name), types.FunctionType):
        #         start_idx += 1

        #     def inner(args):
        #         kwargs = {
        #             key: getattr(args, key)
        #             for key in list(inspect.signature(func).parameters)[start_idx:]
        #         }
        #         return kwargs

        #     return inner

        # parser.set_defaults(
        #     command=command,
        #     process_kwargs=getter("process"),
        #     glob_kwargs=getter("glob"),
        #     filter_kwargs=getter("filter"),
        #     init_kwargs=getter("initialize"),
        # )


parser = Parser()
