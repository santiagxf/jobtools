import argparse
import importlib
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path
from jobtools.runner import TaskRunner

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        module_path = sys.argv[1]
        method = sys.argv[2]
    else:
        parser = argparse.ArgumentParser('jobtools')
        parser.add_argument("file.py", help='path to the Python source file')
        parser.add_argument("MyTask", help='name of the function to call')
        parser.parse_known_args()
    
    if module_path.endswith('.py'):
        if not Path(module_path).exists():
            raise FileNotFoundError(module_path)
        
        module_name = Path(module_path).stem
        modulevar = SourceFileLoader(module_name, module_path).load_module()
    else:
        module_spec = importlib.util.find_spec(module_path)
        modulevar = module_spec.loader.load_module()
    
    callable_func = getattr(modulevar, method)

    tr = TaskRunner(ignore_arguments = sys.argv[1:3])
    tr.run(callable_func)
    
    exit(0)
