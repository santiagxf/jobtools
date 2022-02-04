# jobtools

This package contains a convenient way to invoke `Python` code from the command line to execute jobs of any kind.

## General idea

To run a `Python` file from the command line you can do something like `python task.py`, considering that you have a file called `task.py`. However, if you routine needs parameters, then you have to do all the parsing of the arguments by hand. This has some limitations:
- Naming conventions in bash or Windows Command line are different. For instance parameters in bash are usually indicated as `--my-parameter` while in `Python` the `-` character is not valid. 
- Type parsing has to be done by hand with `argparser`.
- Complex types are hard to indicate.

This leads to a lot of repetitive code being done each time you want to execute code in `Python` from the command line. This library seeks to help to do:
 - Automatic parameters parsing.
 - Automatic enforcement and detection of optional paramters.
 - Automatic naming convention matching (args like `--my-parameter` are passed as `my_parameter`).
 - Support for some complex types.

## How 
The code that you want to execute will be indicated in a callable function.Arguments for the callable are automatically parsed from the command line and enforced depending on if they are required of not. Paramters with default value are inferred to be optional while paramters without one are required. Type conversion is automatically handled. Special type conversion is supported for aruments of type `SimpleNamespace` which can be passed as arguments using `YML` or `JSON` files.

## Usage

`task.py`
```python
import jobtools
from types import SimpleNamespace

def mytask(name: str, max_buffer: int, params: SimpleNamespace, optional_arg: int = 10) -> int:
    """
    This is the function you want to run
    """
    ...
    text = f'Paramters are automatically parse so I can use {name}. Since params \
             is a `SimpleNamespace` argument, then the `YML` file structure will \
             be mapped. I can use {params.trips.origin} and {params.trips.destiny} \
             including {params.budget}.'
    print(text)

    return ...

if __name__ == "__main__":
    tr = jobtools.runner.TaskRunner()
    result = tr.run(mytask)
```

Then this file can be called as:

```bash
python task.py --name "my name" --max-buffer 1024 --params params.yml
```

or

```bash
python task.py --name "my name" --max-buffer 1024 --params params.yml --optional-arg 15
```


The corresponding `YML` file would be like:

`params.yml`
```yaml
trips:
    origin: 'BUE'
    destinty: 'SFO'
budget: 700
```

### Using enumerators as arguments

You can use enumerators as paramters of your jobs. This results handy when you want to enforce specific values instead of handling strings as paramters. You can indicate a parameters as an enumerator using the class `jobtools.arguments.StringEnum` like follows:

```python
import jobtools
from types import SimpleNamespace
from jobtools.arguments import StringEnum

class CompareStrategy(StringEnum):
    BIGGER_BETTER = 'Bigger is better'
    SMALLER_BETTER = 'Smaller is better'

def mytask(name: str, logic: CompareStrategy = CompareStrategy.BIGGER_BETTER) -> int:
    """
    This is the function you want to run
    """
    ...
    
    if logic == CompareStrategy.BIGGER_BETTER:
        ...

    return ...

if __name__ == "__main__":
    tr = jobtools.runner.TaskRunner()
    result = tr.run(mytask)
```

Then this file can be called as:

```bash
python task.py --name "my name" --logic "Bigger is better"
```

The values in the argument `logic` needs to be any of the choices in the enum indicated in the type. This is automatically enforced.