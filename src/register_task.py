import subprocess

# $Action = New-ScheduledTaskAction `
#     -Execute 'PowerShell.exe' `
#     -Argument '-File "C:\Scripts\MyScript.ps1"'

# $Trigger = New-ScheduledTaskTrigger `
#     -Daily -At 7:00AM

# $Settings = New-ScheduledTaskSettingsSet `
#     -AllowStartIfOnBatteries `
#     -DontStopIfGoingOnBatteries `
#     -StartWhenAvailable

# Register-ScheduledTask `
#     -Action $Action `
#     -Trigger $Trigger `
#     -Settings $Settings `
#     -TaskName "My Daily Script Task" `
#     -Description "Runs my PowerShell script daily at 7:00 AM"

result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)


def register_task():
    pass

def check_if_scheduled(taskName):
    # $TaskName = "My Daily Script Task"
    # Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue)
    result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True)