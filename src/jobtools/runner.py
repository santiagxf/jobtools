"""
This module provides orchestration to run and execute Python Jobs from the command line
"""
from typing import Callable, Any, List
from jobtools.arguments import TaskArguments, get_args_from_signature, get_parser_from_signature
from jobtools.joblogger import get_logger

class TaskRunner():
    """
    Allows an easy way to run a task in Azure ML and log any input into the run. Tasks are
    specified a callable with arguments that are automatically parsed from the signature. The
    method should return a dictionary with keys "metrics", "arguments" and "artifacts".
    """

    def __init__(self, name: str, args: TaskArguments = None, ignore_arguments: List[str] = None,
                 debug: bool = False) -> None:
        """
        Initializes the TaskRunner. If `args` is indicated, then the argument's won't be parsed
        from the command line. Otherwise they will.

        Parameters
        ----------
        name: str
            Name of the module or task to run. This property can be any string value.
        args: TaskArguments
            Use args when you are using `TaskRunner` directly in Python instead of from the command
            line. When this argument is indicated, no parsing from command line will happen.
        ignore_arguments: List[str]
            Arguments that will be present in the command line but should not be used or enforced
            for the task that will be executed. Defaults to none. This parameter has no effect if
            `args` is indicated.
        debug: bool
            Indicates if debug information should be displayed
        """
        self.name = name
        self.task_arguments = args
        self.ignore_arguments = ignore_arguments or []
        self.debug = debug
        self._logger = get_logger(name, debug)

    def run(self, task: Callable[[], Any]) -> Any:
        """
        Runs the given task specified as a method. Arguments are determined from the signature of
        the method and they should match the arguments indicated in the command line unless they
        are indicated using the `args` arguments during `init`.

        Parameters
        ----------
        task: Callable[[], Dict[TaskResultKey, Dict[str, Any]]]
            The task you want to run. This method can be any that returns a dictionary with keys
            `arguments`, `metrics` and `artifacts`. Parameters for this method will either be
            demanded from the command line or have to be indicated in the constructor of the
            `TaskRunner` object.
        """
        if self.task_arguments is None:
            args = get_args_from_signature(task, self.ignore_arguments)
        else:
            args = self.task_arguments.resolve_for_method(task)

        for key, value in args.items():
            self._logger.debug(f"Argument {key} = {str(value)}")

        self._logger.debug(f"Running method -> {task.__name__}")
        return task(**args)

    def display_help(self, task: Callable[[], Any]) -> None:
        """
        Displays the help for a given method

        Parameters
        ----------
        task : Callable[[], Any]
            The task or method you want to display help for.
        """
        parser = get_parser_from_signature(task, self.ignore_arguments)
        parser.print_help()
