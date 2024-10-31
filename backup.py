import os
import yaml
from rclone_python import rclone
from datetime import datetime


def get_hourly_dir():
    hour = str(datetime.now().hour).zfill(2)
    if hour == '00': 
        return '/hourly.00/'
    elif hour in ['12', '16', '20', '00']:
        return '/hourly.' + hour + '/'
    else: 
        return None


def backup_directory(source, destination, directory):

    day_updated = False
    week_updated = False
    month_updated = False

    # ------------------------------------------------------------------
    # 0. Load the configuration and define some operations
    
    with open('backup.yaml', 'r') as f:
        config = yaml.safe_load(f)

    def accumulate(a, b):
        rclone.copy(
            os.path.join(destination, a, directory),
            os.path.join(destination, b, directory),
            args=['--ignore-existing']
        )

    def replace(a, b):
        rclone.move(
            os.path.join(destination, a, directory),
            os.path.join(destination, b, directory)
        )

    # ------------------------------------------------------------------
    # 1. Sync destination with source and save the incremental output in /temp

    rclone.sync(
        source, 
        os.path.join(destination, 'temp', directory),
        args=['--fast-list','--delete-excluded','--links',
              f'--backup-dir {destination}temp/{directory}']
    )

    # ------------------------------------------------------------------
    # 2. Save the backup in the hourly backup
    
    if hourly_dir := get_hourly_dir():
        rclone.copy(
            os.path.join(destination, 'temp', directory),
            os.path.join(destination, hourly_dir, directory)
        )

    # ------------------------------------------------------------------
    # 3. Update the DAILY backups

    if (day := datetime.now().weekday()) != config['last_backup']['daily']:
        replace('daily.2', 'daily.3')
        replace('daily.1', 'daily.2')
        config['last_backup']['daily'] = day
        day_updated = True
    accumulate('temp', 'daily.1')

    # ------------------------------------------------------------------
    # 4. Update the WEEKLY backups

    if (week := datetime.now().isocalendar()[1]) != config['last_backup']['weekly']:
        replace('weekly.1', 'weekly.2')
        config['last_backup']['weekly'] = week
    if day_updated:
        accumulate('daily.1', 'weekly.1')

    # ------------------------------------------------------------------
    # 5. Update the MONTHLY backups

    if (month := datetime.now().strftime("%B")) != config['last_backup']['monthly']:
        replace('monthly.2', 'monthly.3')
        replace('monthly.1', 'monthly.2')
        config['last_backup']['monthly'] = month
    if week_updated:
        accumulate('weekly.1', 'monthly.1')

    # ------------------------------------------------------------------
    # 6. Update the YEARLY backups

    if (year := datetime.now().year) != config['last_backup']['yearly']:
        replace('yearly.1', 'yearly.2')
        config['last_backup']['yearly'] = year
    if month_updated:
        accumulate('montly.1', 'yearly.1')

    # ------------------------------------------------------------------
    # 7. Save the configuration

    with open('backup.yaml', 'w') as f:
        yaml.dump(config, f)


if __name__ == '__main__':

    # Load the configuration
    with open('backup.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Backup all directories for each remote
    for remote in config['remotes']:
        for directory, source in config['directories'].value:
            backup_directory(source, remote, directory)
            print(f'[{datetime.now()}] "{directory}" was backed up on "{remote}"')