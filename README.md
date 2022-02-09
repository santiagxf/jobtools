# jobtools

This package contains a convenient way to invoke `Python` code from the command line to execute jobs of any kind.

## General idea

To run a `Python` file from the command line you can do something like `python task.py`, considering that you have a file called `task.py`. However, if you routine needs parameters, then you have to do all the parsing of the arguments by hand. This has some limitations:
- Naming conventions in bash or Windows Command line are different. For instance parameters in bash are usually indicated as `--my-parameter` while in `Python` the `-` character is not valid. 
- Type parsing has to be done by hand with `argparser`.
- Complex types are hard to indicate.

This leads to a lot of repetitive code being done each time you want to execute code in `Python` from the command line. This library seeks to help to do:
 - Automatic parameters parsing.
 - Automatic enforcement and detection of optional parameters.
 - Automatic naming convention matching (args like `--my-parameter` are passed as `my_parameter`).
 - Support for some complex types.

## How 
The code that you want to execute will be indicated in a callable function. Arguments for the callable are automatically parsed from the command line and enforced depending on if they are required or not. Parameters with a default value are inferred to be optional while parameters without one are marked required. Type conversion is automatically handled. Special type conversion is supported for aruments of type `SimpleNamespace` which can be passed as arguments using `YML` or `JSON` files. Enumerators are also supported as arguments. See [Using enumerators as arguments](#Using-enumerators-as-arguments) for details.

## Usage

`task.py`
```python
from types import SimpleNamespace

def mytask(name: str, max_buffer: int, params: SimpleNamespace, optional_arg: int = 10) -> int:
    """
    This is the function you want to run
    """
    ...
    text = f'parameters are automatically parse so I can use {name}. Since params \
             is a `SimpleNamespace` argument, then the `YML` file structure will \
             be mapped. I can use {params.trips.origin} and {params.trips.destiny} \
             including {params.budget}.'
    print(text)

    return ...
```

Then this file can be called using the command `jobtools` or `pyrunit` (they are aliases):

```bash
pyrunit task.py mytask --name "my name" --max-buffer 1024 --params params.yml
```

or

```bash
pyrunit task.py mytask --name "my name" --max-buffer 1024 --params params.yml --optional-arg 15
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

You can use enumerators as parameters of your jobs. This results handy when you want to enforce specific values instead of handling strings as parameters. You can indicate a parameters as an enumerator using the class `jobtools.arguments.StringEnum` like follows:

```python
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
```

Then this file can be called as:

```bash
pyrunit task.py mytask --name "my name" --logic "Bigger is better"
```

The values in the argument `logic` needs to be any of the choices in the enum indicated in the type. This is automatically enforced.

### Displaying help

You can display help about how to run an specific function by using the flag `--help` or `-h`. Note how argument typing help is also provided including: possible values for enums, type hints and optional vs required arguments.

```bash
> pyrunit task.py mytask --help

usage: pyrunit task.py mytask [-h] --integer INTEGER --decimal DECIMAL --compare-strategy {Bigger is better,Smaller is better} [--boolean BOOLEAN]

positional arguments:
  task_types.py
  mytask

arguments:
  -h, --help            show this help message and exit
  --integer INTEGER     of type int
  --decimal DECIMAL     of type float
  --compare-strategy {Bigger is better,Smaller is better}

optional arguments:
  --boolean BOOLEAN     of type bool
```
