from src.backup import *

def test_config():
    with open('backup.yaml', 'r') as f:
        config = yaml.safe_load(f)

    assert config.keys() == {'directories', 'remotes', 'last_backup'}
    assert config['last_backup'].keys() == {'daily', 'weekly', 'monthly', 'yearly'}

def test_get_hourly_dir():
    assert get_hourly_dir('00') == 'hourly.24'
    assert get_hourly_dir('04') == None
    assert get_hourly_dir('08') == None
    assert get_hourly_dir('12') == 'hourly.12'
    assert get_hourly_dir('16') == 'hourly.16'
    assert get_hourly_dir('20') == 'hourly.20'

def test_accumulate():
    pass

def test_replace():
    pass