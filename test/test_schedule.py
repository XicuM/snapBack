import sys
import pytest
from src.schedule import *

# Skip the test if the platform is not Windows
pytestmark = pytest.mark.skipif(
    sys.platform != 'win32', 
    reason='Test runs only on Windows'
)


def is_task_scheduled(task_name):
    output, _ = run_powershell_command(f'''
        $result = Get-ScheduledTask `
            -taskName "{task_name}" `
            -ErrorAction SilentlyContinue
        if ($result) {{ $true }} else {{ $false }}
    ''')
    return output.strip() == 'true'


def delete_task(task_name):
    run_powershell_command(f'''
        Unregister-ScheduledTask `
        -task_name "{task_name}" `
        -Confirm:$false
    ''')


def test_schedule_task(): # TODO: this will fail if the task is already scheduled
    
    # Schedule the backup tasks
    schedule_tasks()
    
    for hour in HOURS:
        task_name = 'backup.'+hour

        # Check if the task is scheduled
        assert (
            is_task_scheduled(task_name), 
            f'Task {task_name} was not found.'
        )
        
        # Delete the task
        delete_task(task_name)
        assert (
            not is_task_scheduled(task_name), 
            f'Task {task_name} was not deleted.'
        )