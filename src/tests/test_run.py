import subprocess

def test_yaml_loading():
    result = subprocess.run(["python", "tests/task_print.py", "--name", "sometext" ,"--params" ,"tests/params.yml"], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')

    assert output == "Name is sometext\n"
    assert result.returncode == 8 # 6 + 2. The sum of the numbers is returned

def test_yaml_folder_loading():
    result = subprocess.run(["python", "tests/task_print.py", "--name", "sometext" ,"--params" ,"tests"], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')

    assert output == "Name is sometext\n"
    assert result.returncode == 8 # 6 + 2. The sum of the numbers is returned

def test_lists():
    result = subprocess.run(["python", "tests/task_lists.py", "--lists", "lala, pepe"], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')

    assert result.returncode == 2 # len of the list

def test_type_conversions():
    result = subprocess.run(["python", "tests/task_types.py", "--integer", "10" ,"--decimal" ,"10.5", "--compare-strategy", "Bigger is better"], stdout=subprocess.PIPE)
    assert result.returncode == 0