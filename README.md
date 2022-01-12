# jobtools

This package contains a convenient implementation to work with `Python` from a command line to execute jobs of any kind. Jobs are indicated using a callable function that the `TaskRunner` can executed. Arguments for the callable are automatically parsed from the command line and enforced depending on if they are required of not. Type conversion is automatically handled. Special type conversion is supported for aruments of type `SimpleNamespace` which can be passed as arguments using `YML` or `JSON` files.

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
    ...

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