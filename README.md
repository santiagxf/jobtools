[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI/CD](https://github.com/santiagxf/jobtools/actions/workflows/python-publish.yml/badge.svg)](https://github.com/santiagxf/jobtools/actions/workflows/python-publish.yml)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/santiagxf/jobtools)
# jobtools

This package contains a convenient way to invoke `Python` code from the command line to execute jobs of any kind.

## General idea

To run a `Python` file from the command line you can do something like `python task.py`, considering that you have a file called `task.py`. However, if you routine needs parameters, then you have to do all the parsing of the arguments by hand. This has some limitations:
- Naming conventions in bash or Windows Command line are different. For instance parameters in bash are usually indicated as `--my-parameter` while in `Python` the `-` character is not valid. 
- Type parsing has to be done by hand with `argparser`.
- It requires to handle how the file is invoked.
- Complex types are hard to indicate.

This leads to a lot of repetitive code being done each time you want to execute code in `Python` from the command line. This library seeks to help to do:
 - Automatic parameters parsing.
 - Automatic enforcement and detection of optional parameters.
 - Automatic naming convention matching (args like `--my-parameter` are passed as `my_parameter`).
 - Support for some complex types.

## How 
The code that you want to execute will be indicated in a callable function. Arguments for the callable are automatically parsed from the command line and enforced depending on if they are required or not. Parameters with a default value are inferred to be optional while parameters without one are marked required. Type conversion is automatically handled using type hints. Special type conversion is supported for arguments of type `SimpleNamespace` which can be passed as arguments using `YML` or `JSON` files. Enumerators are also supported as arguments. See [Using enumerators as arguments](#Using-enumerators-as-arguments) for details.

### How is `jobtools` different from [`click`](https://click.palletsprojects.com/)?

At first, `jobtools` may look very similar to `click`. However, `click` is intended to create command line tools using Python. That means that the code that you are writing has to be modified to meet `click` requirements. You source code is coupled with the way `click` works (you will import `click` in your namespace, add decorators, etc). On the other hand, `jobtools` is intended to be  generic way to execute Python code from the command line. No modifications shall be made to the source code in order to execute the code using `jobtools` (besides adding type hints). Some advance features, like enums, may be facilitated by importing `jobtools` but it is not required as you can implement enumerators in your code in a native Pythonic way. Then, you code can be completely decoupled from `jobtools`.

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
jobtools task.py mytask --name "my name" --max-buffer 1024 --params params.yml
```

or

```bash
jobtools task.py mytask --name "my name" --max-buffer 1024 --params params.yml --optional-arg 15
```

The corresponding `YML` file would be like:

`params.yml`
```yaml
trips:
    origin: 'BUE'
    destiny: 'SFO'
budget: 700
```
#### Other ways to run it
Both `jobtools` and `pyrunit` are bash scripts installed by pipx. If you environment cannot access them because of how it is set, then you have alternatives:

1. As a `Python` module:
    ```bash
    python -m jobtools task.py MyTask --arg1 value1
    ```

2. Handling the execution yourself:

    ```bash
    python task.py --arg1 value1
    ```

    In your `Python` script add:

    ```python
    from jobtools.runner import TaskRunner

    def MyMethod(arg1: str):
      (...)

    if __name__ == "__main__":
      tr = TaskRunner()
      tr.run(MyMethod)
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
jobtools task.py mytask --name "my name" --logic "Bigger is better"
```

The values in the argument `logic` needs to be any of the choices in the enum indicated in the type. This is automatically enforced.

### Running functions in packages/modules (new in version 0.0.12)

Sometimes, you code is packaged inside of a Python package or module. In the following example, assuming that you have a module that can be loaded from the path you are currently located, you can use `jobtools` to run them using the following sintax:

```bash
jobtools mypkg.mymodule.mysubmod my_task --arg1 value1 --arg2 value2
```

> The package should be resolvable from the location you are invoking the method. If it is a local package, then you should be placed outside of the package itself.

### Loading and saving configuration files from `YAML` and `JSON` (new in version 0.0.14)

`jobtools` extends the support of `SimpleNamespace` in the class `ParamsNamespace` which supports loading and writing configuration files directly. This is useful when authoring the configuration files in Jupyter Notebooks for instance. You can construct the configuration and save it like this:

```python
from jobtools.arguments import ParamsNamespace

params = ParamsNamespace()
params.argument1 = 123
params.argument2 = "this is a string"
params.save('params.yml')
```

In the same way, loading can be done with:

```python
from jobtools.arguments import ParamsNamespace

ParamsNamespace.load('params.yml)
```

> Note that this functionality is added mostly for helping unit testing or fast creation of configuration files. We do not recommend loading configuration files manually, but to rely on using parameters of type `SimpleNamespace` which `jobtools` automatically map to configuration files.

### Displaying help

You can display help about how to run an specific function by using the flag `--help` or `-h`. Note how argument typing help is also provided including: possible values for enums, type hints and optional vs required arguments.

```bash
> jobtools task.py mytask --help

usage: jobtools task.py mytask [-h] --integer INTEGER --decimal DECIMAL --compare-strategy {Bigger is better,Smaller is better} [--boolean BOOLEAN]

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

## Contributing

Ideas and contributions are more than welcome!