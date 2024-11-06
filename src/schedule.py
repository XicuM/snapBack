import subprocess


PROJECT_DIR = r'$env:USERPROFILE\Documents\projects\backups'
HOURS = ['00', '12', '16', '20']


def run_powershell_command(command):
    result = subprocess.run(
        ['powershell', '-Command', command, '-Verb', 'runAs'],
        capture_output=True,
        text=True
    )
    return result.stdout, result.stderr


def schedule_tasks():

    define_action = rf'''
        $Action = New-ScheduledTaskAction `
            -Execute "python" `
            -Argument "src\backup.py"
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
            -DontStopIfGoingOnBatteries `
            -StartWhenAvailable

        Register-ScheduledTask `
            -Action $Action `
            -Trigger $Triggers `
            -Settings $Settings `
            -TaskName "backups" `
            -Description "Runs daily backups for my documents"
    '''

    run_powershell_command(
        define_action + 
        create_trigger_list + 
        ''.join(define_trigger(hour) for hour in HOURS) + 
        register_task
    )

if __name__ == '__main__':
    schedule_tasks()