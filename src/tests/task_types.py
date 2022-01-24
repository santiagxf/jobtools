import jobtools

def mytask(integer: int, decimal: float) -> int:
    assert isinstance(integer, int)
    assert isinstance(decimal, float)
    assert decimal > int(decimal)

    return 0

if __name__ == "__main__":
    tr = jobtools.runner.TaskRunner()
    exit(tr.run(mytask))