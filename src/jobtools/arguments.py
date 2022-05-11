"""
Provides a convenient way to read and parse arguments for Python scripts being run using
the command line.
"""

import pathlib
import logging
import argparse
import inspect
from enum import Enum
from types import SimpleNamespace
from typing import Callable, Dict, Any, List

import json
import yaml

class ExtNamespace(SimpleNamespace):
    """
    Extends the functionality of a SimpleNamespace for holding configuration.
    """
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def __iter__(self):
        return self.__dict__

    def to_dict(self) -> Dict[str, Any]:
        """
        Returns a dictionary representation of the object.

        Returns
        -------
        Dict[str, Any]
            Dictionary of values
        """
        def _to_dict(ns: SimpleNamespace):
            converted = ns.__dict__

            for key in converted.keys():
                if isinstance(converted[key], SimpleNamespace):
                    converted[key] = _to_dict(converted[key])
            
            return converted

        return _to_dict(self)


class StringEnum(Enum):
    """
    Represents enums with string associated values.
    """
    def __str__(self):
        return str(self.value)

def str2bool(value: str) -> bool:
    """
    Parses an string representing a boolean value to its corresponding
    value.

    Parameters
    ----------
    value : str
        The boolean value as string. Possible values are
        ['yes', 'true', 't', 'y', '1'/'-1'] or ['no', 'false', 'f', 'n', '0']

    Returns
    -------
    bool
        The corrresponding boolean value

    Raises
    ------
    argparse.ArgumentTypeError
        If values are not in the possible values.
    """
    if isinstance(value, bool):
        return value
    if value.lower() in ('yes', 'true', 't', 'y', '1', '-1'):
        return True
    elif value.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError(f"Unable to understand '{value}' as boolean.")

def delimited2list(delimited: str, delimiter: str = ',') -> List[str]:
    """
    Parses a delimited list encoded as string to a list of string

    Parameters
    ----------
    delimited : str
        The argument containing string values delimited by comma.
    delimiter: str
        The delimiter

    Returns
    -------
    List[str]
        Parsed output
    """
    return [item.strip() for item in delimited.split(delimiter)]

def file2namespace(config_file_path: str, default_extension: str = 'yml') -> ExtNamespace:
    """
    Loads a `YAML` or `JSON` file containing representing configuration and parses
    it as a `SimpleNamespace` object. If the path is a directory, the first file with extension
    `YAML` or `JSON` is loaded.

    Parameters
    ----------
    config_file_path : str
        Path where the `YAML` or `JSON` file is located.

    default_extension: str
        If `config_file_path` is a directory, indicates the extension of the file to look for.
        Defautls to 'yml`.

    Returns
    -------
    ExtNamespace
        The given configuration parsed as a namespace.
    """
    try:
        config_path = pathlib.Path(config_file_path)
        if config_path.is_dir():
            logging.warning(f"[WARN] Configuration path '{config_file_path}' is a directory, \
                            but a yml file is expected. Looking for the first file")
            config_path = next(config_path.glob(f'*.{default_extension}'))

            if not config_path:
                raise FileNotFoundError(f"Unable to find a `{default_extension}` file under directory {config_file_path}")

        with open(str(config_path), encoding='utf-8') as file:
            if config_path.suffix == ".json":
                config = json.load(file)
            elif config_path.suffix == ".yml" or config_path.suffix == ".yaml":
                config = yaml.load(file, Loader=yaml.FullLoader)
            else:
                TypeError(f"File {config_file_path} type is not supported. Only `JSON` or `YML`")

        # This conversion allows to parse nested dictionaries into a Namespace.
        namespace = json.loads(json.dumps(config),
                               object_hook=lambda item: ExtNamespace(**item))
        return namespace

    except RuntimeError as err:
        msg = f"When loading the configuration file from '{config_file_path}', \
                the following error happened: {err}"
        print(msg)
        raise argparse.ArgumentTypeError(msg)

def get_parser_from_signature(method: Callable, extra_arguments: List[str] = []) -> argparse.ArgumentParser:
    """
    Automatically parses all the arguments to match an specific method. The method should
    implement type hinting in order for this to work. All arguments required by the method
    will be also required by the parser. To match bash conventions, arguments with underscore
    will be parsed as arguments with upperscore. For instance `from_path` will be requested
    as `--from-path`. Signature arguments with type `SimpleNamespace` have to be specified
    using a `YAML` file.

    Parameters
    ----------
    method: Callable
        The method the arguments should be extracted from.
    extra_arguments: List[str]
        Indicates extra arguments that are not present in the signature but should be
        included in the returned parser. Use this argument to include other paramters
        that are indicated in the command line but they are used for another purpoise
        and not meant to be sent to the method.

    Returns
    -------
    argparse.ArgumentParser
        The parser to get the arguments from the signature.
    """
    parser = argparse.ArgumentParser("pyrunit")
    required_parser = parser.add_argument_group('required arguments')
    fullargs = inspect.getfullargspec(method)
    args_annotations = dict(filter(lambda key: key[0] != 'return', fullargs.annotations.items()))

    for extra_arg in extra_arguments:
        parser.add_argument(extra_arg, type=str, )

    required_args_idxs = len(args_annotations) - len(fullargs.defaults if fullargs.defaults else [])
    for idx, (arg, arg_type) in enumerate(args_annotations.items()):
        is_required = idx < required_args_idxs
        assigned_parser = required_parser if is_required else parser
        argument_flag = f"--{arg.replace('_','-')}"
        if isinstance(arg_type, type):
            if issubclass(arg_type, SimpleNamespace):
                if not is_required:
                    raise ValueError("An argument of type SimpleNamespace can't be optional.\
                        Remove default values.")
                assigned_parser.add_argument(argument_flag,
                                    dest=arg,
                                    type=file2namespace,
                                    required=is_required,
                                    help='indicated as a YAML or JSON file')
            elif issubclass(arg_type, Enum):
                assigned_parser.add_argument(argument_flag,
                                    dest=arg,
                                    type=arg_type,
                                    choices=list(arg_type),
                                    required=is_required)
            elif issubclass(arg_type, bool):
                assigned_parser.add_argument(argument_flag,
                                    dest=arg,
                                    type=str2bool,
                                    required=is_required,
                                    help=f"of type {arg_type.__name__}")
            else:
                assigned_parser.add_argument(argument_flag,
                                    dest=arg,
                                    type=arg_type,
                                    required=is_required,
                                    help=f"of type {arg_type.__name__}")
        else:
            try:
                if arg_type._name == 'List' or arg_type._name == 'Dict':
                    assigned_parser.add_argument(argument_flag,
                                        dest=arg,
                                        type=delimited2list,
                                        required=is_required,
                                        help=f"indicated as a comma separted string")
                else:
                    raise TypeError(f'Type {arg_type} is not supported in this version of jobtools')
            except RuntimeError:
                raise TypeError(f'Type {arg_type} is not supported in this version of jobtools')

    return parser

def get_args_from_signature(method: Callable, extra_arguments: List[str] = []) -> Dict[str, Any]:
    """
    Automatically parses all the arguments to match an specific method. The method should
    implement type hinting in order for this to work. All arguments required by the method
    will be also required by the parser. To match bash conventions, arguments with underscore
    will be parsed as arguments with upperscore. For instance `from_path` will be requested
    as `--from-path`. Signature arguments with type `SimpleNamespace` have to be specified
    using a `YAML` file.

    Parameters
    ----------
    method: Callable
        The method the arguments should be extracted from.

    Returns
    -------
    Dict[str, Any]
        The arguments parsed. You can call `method` with `**...` then.
    """
    parser = get_parser_from_signature(method, extra_arguments)

    arguments_dict = vars(parser.parse_args())
    for extra_arg in extra_arguments:
        arguments_dict.pop(extra_arg)

    return arguments_dict

class TaskArguments():
    """
    Provides a way to run the `TaskRunner` without executing Python code from
    Python command line. So running `python myfile.py --arg1 value1 --arg2 value2`
    is equivalent to `TaskArguments(arg1=value1, arg2=value2)`.
    """
    def __init__(self, **args):
        self.args = args

    def get_args(self) -> Dict[str, Any]:
        """
        Gets current arguments in task
        """
        return self.args

    def resolve_for_method(self, method: Callable) -> Dict[str, Any]:
        """
        Evaluates the given arguments against a given signature and ensures
        you can call the method using the indicated arguments.

        Parameters
        ----------
        method: Callabale
            The method that the arguments need to match.

        Returns
        -------
        Dict[str, Any]:
            The arguments that will be indicated to the method with their corresponding typing
            conversion in case requried.
        """
        fullargs = inspect.getfullargspec(method)
        args_annotations = dict(filter(lambda key: key[0] != 'return',
                                fullargs.annotations.items()))
        parsed_args = {}

        required_args_idxs = len(args_annotations) \
            - len(fullargs.defaults if fullargs.defaults else [])
        for idx, (arg_name, arg_type) in enumerate(args_annotations.items()):
            is_required = idx < required_args_idxs

            if is_required and arg_name not in self.args.keys():
                ValueError(f"Parameter {arg_name} is not optional")

            if arg_type is type(self.args[arg_name]):
                parsed_args[arg_name] = self.args[arg_name]
            elif issubclass(arg_type, SimpleNamespace) and self.args[arg_name] is str:
                parsed_args[arg_name] = file2namespace(self.args[arg_name])
            else:
                raise ValueError(f"Parameter {arg_name} is expecting {arg_type} but got \
                    {type(self.args[arg_name])} which is incompatible.")

        return parsed_args
