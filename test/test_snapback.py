import os
import shutil
import time
from src.snapback import *
from os.path import join, exists


# Define the source and destination directories for testing
DIRECTORY = 'directory'
SOURCE = join('test', 'test_data', 'source')
DESTINATION = join('test', 'test_data', 'destination')
BACKUP_DIR = join(DESTINATION, '.snapbacks', DIRECTORY)

# Auxiliary functions

def new_file(path, name, content=''):
    if not exists(path): os.makedirs(path)
    with open(join(path, name+'.txt'), 'w') as f: f.write(content)

def assert_file_content(file, content, message=None):
    with open(file, 'r') as f:
        assert (f.read() == content), message

def assert_file_exists(dir, file):
    assert (
        exists(join(dir, file+'.txt')), 
        f'File {file} should exist in {dir}'
    )

def assert_file_not_exists(dir, file):
    assert (
        not exists(join(dir, file+'.txt')), 
        f'File {file} should not longer exist in {dir}'
    )

def rmdirs(*dirs): return (shutil.rmtree(dir) for dir in dirs)


def test_config():
    '''
    Check if the configuration file is correctly loaded
    '''
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    assert (
        config.keys() == {'directories', 'remotes', 'last_backup'}, 
        'Configuration file should have directories, remotes, and last_backup keys'
    )
    assert (
        config['last_backup'].keys() == {'daily', 'weekly', 'monthly', 'yearly'},
        'last_backup should have daily, weekly, monthly, and yearly keys'
    )


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


def test_accumulate():
    '''
    In this test, the expected behaviour is to accumulate the contents 
    of the .temp directory into the daily.1 directory: AB + A' = AB
    '''
    # Create the necessary directories and files
    new_file(join(BACKUP_DIR,'.temp'),   'A', 'File A: New content')
    new_file(join(BACKUP_DIR,'.temp'),   'B', 'File B')
    time.sleep(1)
    new_file(join(BACKUP_DIR,'daily.1'), 'A', 'File A: Old content')

    # Perform the accumulation
    SnapBack(SOURCE, DESTINATION, DIRECTORY).accumulate('.temp', 'daily.1')

    # Check if the directory was correctly accumulated
    assert_file_not_exists(join(BACKUP_DIR, '.temp'), 'A')
    assert_file_content(
        file=join(BACKUP_DIR, 'daily.1', 'A.txt'),
        content='File A: Old content', 
        message='File A should not be overwritten'
    )
    assert_file_content(
        file=join(BACKUP_DIR, 'daily.1', 'B.txt'),
        content='File B', 
        message='File B should be copied to daily.1'
    )

    # Delete the directories
    rmdirs(join(BACKUP_DIR,'.temp'), join(BACKUP_DIR,'daily.1'))


def test_move():
    '''
    In this test, the expected behaviour is to replace the contents 
    of the .temp directory into the daily.1 directory: AB -> A' = AB
    '''
    # Create the necessary directories and files
    new_file(join(BACKUP_DIR,'daily.1'), 'A', 'File A: Newer content')
    new_file(join(BACKUP_DIR,'daily.1'), 'B', 'File B')
    time.sleep(1)
    new_file(join(BACKUP_DIR,'daily.2'), 'A', 'File A: Older content')

    SnapBack(SOURCE, DESTINATION, DIRECTORY).move('daily.1', 'daily.2')

    # Check if the directory was correctly moved
    assert_file_not_exists(join(BACKUP_DIR, 'daily.1'), 'A')
    assert_file_not_exists(join(BACKUP_DIR, 'daily.1'), 'B')
    assert_file_content(
        file=join(BACKUP_DIR, 'daily.2', 'A.txt'),
        content='File A: Newer content',
        message='File A should not be overwritten'
    )
    assert_file_content(
        file=join(BACKUP_DIR, 'daily.2', 'B.txt'),
        content='File B', 
        message='File B should be copied to daily.1'
    )

    # Delete the directories
    rmdirs(SOURCE, DESTINATION)


def test_sync():
    '''
    Check if the sync function is correctly defined
    '''
    # Create the necessary directories and files
    new_file(join(DESTINATION, DIRECTORY), 'A', 'File A: Older content')
    time.sleep(1)
    new_file(SOURCE, 'A', 'File A: Newer content')
    new_file(SOURCE, 'B', 'File B')

    SnapBack(SOURCE, DESTINATION, DIRECTORY).sync()

    # Check if source remains the same
    assert_file_content(
        file=join(SOURCE, 'A.txt'),
        content='File A: Newer content',
        message='File A should not be moved'
    )
    assert_file_content(
        file=join(SOURCE, 'B.txt'),
        content='File B',
        message='File B should not be moved'
    )

    # Check if the destination was correctly updated
    assert_file_content(
        file=join(join(DESTINATION, DIRECTORY), 'A.txt'),
        content='File A: Newer content',
        message='File A should have been synced'
    )
    assert_file_content(
        file=join(join(DESTINATION, DIRECTORY), 'B.txt'),
        content='File B',
        message='File B should have been synced'
    )

    # Check if the backup directory was correctly updated
    assert_file_content(
        file=join(BACKUP_DIR, '.temp', 'A.txt'),
        content='File A: Older content',
        message='File A should have been backed up to .temp'
    )
    assert_file_not_exists(join(BACKUP_DIR, '.temp'), 'B')
    
    # Delete the directories
    rmdirs(SOURCE, DESTINATION)


def test_update_hourly():
    '''
    Check if the update function is correctly defined for the hourly backups
    '''
    # Create the necessary directories and files
    new_file(join(DESTINATION, DIRECTORY), 'A', 'File A: Old content')
    new_file(SOURCE, 'A', 'File A: New content')
    for hour in HOURS:
        SnapBack(SOURCE, DESTINATION, DIRECTORY).update(hour)
        assert_file_exists(join(BACKUP_DIR, get_hourly_dir(hour)), 'A')


def test_update_daily():
    '''
    Check if the update function is correctly defined for the rest of the backups
    '''
    # Create the necessary directories and files
    new_file(join(DESTINATION, DIRECTORY), 'A', 'File A: Old content')
    new_file(SOURCE, 'A', 'File A: New content')

    for i in range(1, 24*4*7*4+1):
        SnapBack(SOURCE, DESTINATION, DIRECTORY).update()
        match i:
            case      1*4: assert_file_exists(join(BACKUP_DIR, 'daily.1'), 'A')
            case      2*4: assert_file_exists(join(BACKUP_DIR, 'daily.2'), 'A')
            case      3*4: assert_file_exists(join(BACKUP_DIR, 'daily.3'), 'A')
            case      7*4: assert_file_exists(join(BACKUP_DIR, 'weekly.1'), 'A')
            case    2*7*4: assert_file_exists(join(BACKUP_DIR, 'weekly.2'), 'A')
            case    4*7*4: assert_file_exists(join(BACKUP_DIR, 'monthly.1'), 'A')
            case  2*4*7*4: assert_file_exists(join(BACKUP_DIR, 'monthly.2'), 'A')
            case 12*4*7*4: assert_file_exists(join(BACKUP_DIR, 'yearly.1'), 'A')
            case 24*4*7*4: assert_file_exists(join(BACKUP_DIR, 'yearly.2'), 'A')


def test_restore():
    '''
    Check if the restore function is correctly defined
    '''
    pass