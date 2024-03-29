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
from jobtools.joblogger import get_logger

import json
import yaml

class ParamsNamespace(SimpleNamespace):
    """
    Extends the functionality of a SimpleNamespace for holding configuration.
    """
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def __iter__(self):
        return self.__dict__.__iter__()

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

    @classmethod
    def load(cls, path: str, default_extension: str = 'yml') -> 'ParamsNamespace':
        """
        Loads a namespace from a `YAML` or `JSON` file

        Parameters
        ----------
        path : str
            Path of the file to load. If a folder is provided,
            then the first file is loaded with extension `default_extension`.
        
        default_extension: str
            If `path` is a directory, indicates the extension of the file to look for.
            Defautls to 'yml`.

        Returns
        -------
        ParamsNamespace
            The namespace representing the given file.

        Raises
        ------
        TypeError
            If `path` has an unsupported file extension.
        """
        return file2namespace(path, default_extension)

    def save(self, path: str):
        """
        Saves the namespace to a file. Support files with
        extensions `YML` or `JSON`.

        Parameters
        ----------
        path : str
            File name where to place the configuration, including extension. Supported
            extensions are `JSON` and `YML`.

        Raises
        ------
        TypeError
            If `config_file_path` has an unsupported file extension.
        """

        full_path = pathlib.Path(path)

        with open(str(full_path), 'w', encoding='utf8') as outfile:
            if full_path.suffix == ".json":
                json.dump(self.to_dict(), outfile, indent=4)
            elif full_path.suffix == ".yml" or full_path.suffix == ".yaml":
                yaml.dump(self.to_dict(), outfile, default_flow_style=False)
            else:
                raise TypeError(f"File {full_path} type is not supported. Only `JSON` or `YML`")

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
        The corresponding boolean value

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

def file2namespace(config_file_path: str, default_extension: str = 'yml') -> ParamsNamespace:
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
        Defaults to 'yml`.

    Returns
    -------
    ParamsNamespace
        The given configuration parsed as a namespace.

    Raises
    ------
    TypeError
        If `config_file_path` has an unsupported file extension.
    """
    try:
        config_path = pathlib.Path(config_file_path)
        if config_path.is_dir():
            get_logger().warning(f"Configuration path '{config_file_path}' is a directory, "
                                 "but a yml file is expected. Looking for the first file")
            config_path = next(config_path.glob(f'*.{default_extension}'))

            if not config_path:
                raise FileNotFoundError(f"Unable to find a `{default_extension}` file under "
                                        "directory {config_file_path}")

        with open(str(config_path), encoding='utf-8') as file:
            if config_path.suffix == ".json":
                config = json.load(file)
            elif config_path.suffix == ".yml" or config_path.suffix == ".yaml":
                config = yaml.load(file, Loader=yaml.FullLoader)
            else:
                raise TypeError(f"File {config_file_path} type is not supported. Only `JSON` "
                                "or `YML`")

        # This conversion allows to parse nested dictionaries into a Namespace.
        namespace = json.loads(json.dumps(config),
                               object_hook=lambda item: ParamsNamespace(**item))
        return namespace

    except RuntimeError as err:
        msg = f"When loading the configuration file from '{config_file_path}', \
                the following error happened: {err}"
        print(msg)
        raise argparse.ArgumentTypeError(msg)

def get_parser_from_signature(method: Callable, extra_arguments: List[str] = None) -> argparse.ArgumentParser:
    """
    Automatically parses all the arguments to match an specific method. The method should
    implement type hinting in order for this to work. All arguments required by the method
    will be also required by the parser. To match bash conventions, arguments with underscore
    will be parsed as arguments with dash (`-`). For instance `from_path` will be requested
    as `--from-path`. Signature arguments with type `SimpleNamespace` have to be specified
    using a `YAML` file.

    Parameters
    ----------
    method: Callable
        The method the arguments should be extracted from.
    extra_arguments: List[str]
        Indicates extra arguments that are not present in the signature but should be
        included in the returned parser. Use this argument to include other parameters
        that are indicated in the command line but they are used for another purpose
        and not meant to be sent to the method.

    Returns
    -------
    argparse.ArgumentParser
        The parser to get the arguments from the signature.
    """
    logger = get_logger()
    parser = argparse.ArgumentParser("jobtools")
    required_parser = parser.add_argument_group('required arguments')
    fullargs = inspect.getfullargspec(method)
    args_annotations = dict(filter(lambda key: key[0] != 'return', fullargs.annotations.items()))

    for arg in fullargs.args:
        logger.debug(f'Signature argument: {arg}')

    if len(args_annotations) != len(fullargs.args):
        missing = [arg for arg in fullargs.args if arg not in fullargs.annotations.keys()]
        raise ValueError(f'Arguments {",".join(missing)}, in method {str(method)}, do not '
                         'have type annotations. Please add them.')

    for extra_arg in extra_arguments:
        parser.add_argument(extra_arg, type=str)

    required_args_idxs = len(args_annotations) - len(fullargs.defaults if fullargs.defaults else [])
    for idx, (arg, arg_type) in enumerate(args_annotations.items()):
        is_required = idx < required_args_idxs
        assigned_parser = required_parser if is_required else parser
        argument_flag = f"--{arg.replace('_','-')}"

        logger.debug(f'Parser argument {arg}: {arg_type.__name__} '
                    f'{"(Required)" if is_required else "(Optional)"})')

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
                                        help="indicated as a comma separated string")
                else:
                    raise TypeError(f'Type {arg_type} is not supported in this version of jobtools')
            except RuntimeError as exc:
                raise TypeError(f'Type {arg_type} is not supported in this '
                                'version of jobtools') from exc

    return parser

def get_args_from_signature(method: Callable, extra_arguments: List[str]) -> Dict[str, Any]:
    """
    Automatically parses all the arguments to match an specific method. The method should
    implement type hinting in order for this to work. All arguments required by the method
    will be also required by the parser. To match bash conventions, arguments with underscore
    will be parsed as arguments with dash (`-`). For instance `from_path` will be requested
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
    parser.add_argument("--debug", help='displays debug information', 
                                   action='store_true',
                                   required=False)

    arguments_dict = vars(parser.parse_args())
    for extra_arg in extra_arguments:
        arguments_dict.pop(extra_arg)

    if "debug" in arguments_dict.keys():
        arguments_dict.pop("debug")

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
        method: Callable
            The method that the arguments need to match.

        Returns
        -------
        Dict[str, Any]:
            The arguments that will be indicated to the method with their corresponding typing
            conversion in case required.
        """
        fullargs = inspect.getfullargspec(method)
        args_annotations = dict(filter(lambda key: key[0] != 'return',
                                fullargs.annotations.items()))

        if len(args_annotations) != len(fullargs.args):
            missing = [arg for arg in fullargs.args if arg not in fullargs.annotations.keys()]
            raise ValueError(f'Arguments {",".join(missing)}, in method {str(method)}, do not '
                             'have type annotations. Annotations are required by jobtools to '
                             'infer types.')

        parsed_args = {}

        required_args_idxs = len(args_annotations) \
            - len(fullargs.defaults if fullargs.defaults else [])
        for idx, (arg_name, arg_type) in enumerate(args_annotations.items()):
            is_required = idx < required_args_idxs

            if is_required and arg_name not in self.args.keys():
                raise ValueError(f"Parameter {arg_name} is required")

            if arg_type is type(self.args[arg_name]):
                parsed_args[arg_name] = self.args[arg_name]
            elif issubclass(arg_type, SimpleNamespace) and self.args[arg_name] is str:
                parsed_args[arg_name] = file2namespace(self.args[arg_name])
            else:
                raise ValueError(f"Parameter {arg_name} is expecting {arg_type} but got \
                    {type(self.args[arg_name])} which is incompatible.")

        return parsed_args
