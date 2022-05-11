from types import SimpleNamespace
from typing import List
import jobtools
from types import SimpleNamespace

def mytask(name: str, params: SimpleNamespace) -> int:
    sum = params.value1 + params.value2
    sum_in_dict = params.to_dict()['group1']['value1'] + params.to_dict()['group1']['value2']

    assert sum == sum_in_dict

    print(f"Name is {name}")
    return sum

if __name__ == "__main__":
    tr = jobtools.runner.TaskRunner()
    exit(tr.run(mytask))