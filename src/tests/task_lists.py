from typing import List
import jobtools

def mytask(lists: List[str] = None) -> int:
    print(len(lists))
    return len(lists)

if __name__ == "__main__":
    tr = jobtools.runner.TaskRunner("test")
    exit(tr.run(mytask))