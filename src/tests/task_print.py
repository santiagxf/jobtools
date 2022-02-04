import jobtools
from types import SimpleNamespace

def mytask(name: str, params: SimpleNamespace) -> int:
    sum = params.value1 + params.value2
    print(f"Name is {name}")
    return sum

if __name__ == "__main__":
    tr = jobtools.runner.TaskRunner()
    exit(tr.run(mytask))