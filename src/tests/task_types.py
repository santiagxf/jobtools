from ast import Compare
import jobtools
from jobtools.arguments import StringEnum

class CompareStrategy(StringEnum):
    BIGGER_BETTER = 'Bigger is better'
    SMALLER_BETTER = 'Smaller is better'

def mytask(integer: int, decimal: float, compare_strategy: CompareStrategy, flag: bool = False) -> int:
    assert isinstance(integer, int)
    assert isinstance(decimal, float)
    assert flag
    assert decimal > int(decimal)
    assert compare_strategy in list(CompareStrategy)
    
    return 0

if __name__ == "__main__":
    tr = jobtools.runner.TaskRunner("test")
    exit(tr.run(mytask))