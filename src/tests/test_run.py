import subprocess

def test_yaml_loading():
    result = subprocess.run(["python", "tests/task.py", "--name", "sometext" ,"--params" ,"tests/params.yml"], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')

    assert output == "Name is sometext\n"
    assert result.returncode == 8 # 6 + 2