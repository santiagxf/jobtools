import argparse
import importlib
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path
from jobtools.runner import TaskRunner
from jobtools.joblogger import get_logger

if __name__ == "__main__":
    if len(sys.argv) < 3:
        parser = argparse.ArgumentParser('jobtools')
        parser.add_argument("file.py", help='path to the Python source file')
        parser.add_argument("MyTask", help='name of the function to call')
        parser.add_argument("--debug", help='displays debug information', action='store_true', required=False)

    MODULE_PATH = sys.argv[1]
    METHOD_NAME = sys.argv[2]
    SYS_ARGS = sys.argv[1:3]
    DEBUG = "--debug" in sys.argv

    if MODULE_PATH.endswith('.py'):
        if not Path(MODULE_PATH).exists():
            raise FileNotFoundError(MODULE_PATH)

        module_name = Path(MODULE_PATH).stem
        loader = SourceFileLoader(module_name, MODULE_PATH)
    else:
        module_name = MODULE_PATH
        module_spec = importlib.util.find_spec(MODULE_PATH)
        loader = module_spec.loader

    logger = get_logger(module_name, DEBUG)
    logger.debug(f'Loading module {module_name}')
    modulevar = loader.load_module()

    callable_func = getattr(modulevar, METHOD_NAME)

    tr = TaskRunner(name=METHOD_NAME, ignore_arguments=SYS_ARGS, debug=DEBUG)
    tr.run(callable_func)

    exit(0)
