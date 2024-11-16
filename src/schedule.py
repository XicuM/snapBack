import subprocess
import yaml
import sys
import os

PROJECT_DIR = os.getcwd()
PYTHON_PATH = sys.executable

with open('config.yaml', 'r') as f:
    HOURS = yaml.safe_load(f)['daily_backup_hours']


def run_powershell_command(command):
    result = subprocess.run(
        ['powershell', '-Command', command],
        capture_output=True,
        text=True
    )
    return result.stdout, result.stderr


def schedule_tasks():

    define_action = rf'''
        $Action = New-ScheduledTaskAction `
            -Execute "{PYTHON_PATH}" `
            -Argument "src\backup.py" `
            -WorkingDirectory "{PROJECT_DIR}"  
    '''
    create_trigger_list = '''
        $Triggers = @()
    '''
    define_trigger = lambda hour: rf'''
        $Triggers += New-ScheduledTaskTrigger `
                -Daily -At {hour}:00
    '''
    register_task = r'''
        $Settings = New-ScheduledTaskSettingsSet `
            -AllowStartIfOnBatteries `
            -StartWhenAvailable:$false `
            -DontStopIfGoingOnBatteries

        Register-ScheduledTask `
            -Action $Action `
            -Trigger $Triggers `
            -Settings $Settings `
            -TaskName "snapBack" `
            -Description "Runs daily backups for my documents"
    '''

    print(run_powershell_command(
        define_action + 
        create_trigger_list + 
        ''.join(define_trigger(hour) for hour in HOURS) + 
        register_task
    )[1])

if __name__ == '__main__':
    schedule_tasks()