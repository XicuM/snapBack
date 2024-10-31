from src.backup import *
from utils import *


def test_config():
    '''
    Check if the configuration file is correctly loaded
    '''
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    assert config.keys() == {'directories', 'remotes', 'last_backup'}
    assert config['last_backup'].keys() == {'daily', 'weekly', 'monthly', 'yearly'}


def test_get_hourly_dir():
    '''
    Check if the correct hourly directory is returned
    '''
    assert get_hourly_dir('00') == 'hourly.24'
    assert get_hourly_dir('04') == None
    assert get_hourly_dir('08') == None
    assert get_hourly_dir('12') == 'hourly.12'
    assert get_hourly_dir('16') == 'hourly.16'
    assert get_hourly_dir('20') == 'hourly.20'


@with_test_directories
def test_accumulate():
    '''
    Check if the accumulate function is correctly defined
    '''
    Backup(
        TEST_SOURCE, TEST_DESTINATION, TEST_DIRECTORY
    ).accumulate('temp', 'daily.1')


@with_test_directories
def test_replace():
    '''
    Check if the replace function is correctly defined
    '''
    Backup(
        TEST_SOURCE, TEST_DESTINATION, TEST_DIRECTORY
    ).replace('temp', 'daily.1')


@with_test_directories
def test_sync():
    '''
    Check if the replace function is correctly defined
    '''
    Backup(
        TEST_SOURCE, TEST_DESTINATION, TEST_DIRECTORY
    ).sync()


@with_test_directories
def test_daily_backups():
    '''
    Check if the daily backups are correctly updated
    '''
    Backup(
        TEST_SOURCE, TEST_DESTINATION, TEST_DIRECTORY
    ).perform()


@with_test_directories
def test_weekly_backups():
    '''
    Check if the weekly backups are correctly updated
    '''
    Backup(
        TEST_SOURCE, TEST_DESTINATION, TEST_DIRECTORY
    ).perform()


@with_test_directories
def test_monthly_backups():
    '''
    Check if the monthly backups are correctly updated
    '''
    Backup(
        TEST_SOURCE, TEST_DESTINATION, TEST_DIRECTORY
    ).perform()


@with_test_directories
def test_yearly_backups():
    '''
    Check if the yearly backups are correctly updated
    '''
    Backup(
        TEST_SOURCE, TEST_DESTINATION, TEST_DIRECTORY
    ).perform()