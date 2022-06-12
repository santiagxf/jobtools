import os
from jobtools.arguments import ParamsNamespace

def test_yaml_loading():
    config = ParamsNamespace.load('tests/params.yml')
    
    assert config is not None
    assert config.value1 == 2
    assert config.value2 == 6
    assert config.group1.value1 == 2
    assert config.group1.value2 == 6

def test_yaml_saving():
    file_path='/tmp/params.yml'
    config = ParamsNamespace.load('tests/params.yml')
    config.save(file_path)
    config = ParamsNamespace.load(file_path)

    assert os.path.exists(file_path)