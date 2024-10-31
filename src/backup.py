import os
import yaml
from rclone_python import rclone
from datetime import datetime


def get_hourly_dir(hour):
    if hour == '00': 
        return 'hourly.24'
    elif hour in ['12', '16', '20', '00']:
        return 'hourly.' + hour
    else: 
        return None
    

class Backup:
    
    def __init__(self, source, destination, directory):
        self.source = source
        self.destination = destination
        self.directory = directory

    def sync(self):
        '''
        Sync the source directory with the destination directory
        '''
        rclone.sync(
            self.source, 
            os.path.join(self.destination, 'temp', self.directory),
            args=['--fast-list','--delete-excluded','--links',
                  f'--backup-dir {self.destination}temp/{self.directory}']
        )

    def accumulate(self, a, b):
        '''
        Accumulate the contents of directory a into directory b
        ignoring existing files (i.e., only new files are copied)
        '''
        rclone.copy(
            os.path.join(self.destination, a, self.directory),
            os.path.join(self.destination, b, self.directory),
            args=['--ignore-existing']
        )
    
    def replace(self, a, b):
        '''
        Replace the contents of directory b with the contents of directory a
        '''
        rclone.move(
            os.path.join(self.destination, a, self.directory),
            os.path.join(self.destination, b, self.directory)
        )

    def perform(self):

        day_updated = False
        week_updated = False
        month_updated = False

        # ------------------------------------------------------------------
        # 0. Load the configuration and define some operations
        
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)

        # ------------------------------------------------------------------
        # 1. Sync destination with source and save the incremental output in /temp
        self.sync()

        # ------------------------------------------------------------------
        # 2. Save the backup in the hourly backup
        
        if hourly_dir := get_hourly_dir(str(datetime.now().hour).zfill(2)):
            rclone.copy(
                os.path.join(self.destination, 'temp', directory),
                os.path.join(self.destination, hourly_dir, directory)
            )

        # ------------------------------------------------------------------
        # 3. Update the DAILY backups

        if (day := datetime.now().weekday()) != config['last_backup']['daily']:
            self.replace('daily.2', 'daily.3')
            self.replace('daily.1', 'daily.2')
            config['last_backup']['daily'] = day
            day_updated = True
        self.accumulate('temp', 'daily.1')

        # ------------------------------------------------------------------
        # 4. Update the WEEKLY backups

        if (week := datetime.now().isocalendar()[1]) != config['last_backup']['weekly']:
            self.replace('weekly.1', 'weekly.2')
            config['last_backup']['weekly'] = week
        if day_updated:
            self.accumulate('daily.1', 'weekly.1')

        # ------------------------------------------------------------------
        # 5. Update the MONTHLY backups

        if (month := datetime.now().strftime("%B")) != config['last_backup']['monthly']:
            self.replace('monthly.2', 'monthly.3')
            self.replace('monthly.1', 'monthly.2')
            config['last_backup']['monthly'] = month
        if week_updated:
            self.accumulate('weekly.1', 'monthly.1')

        # ------------------------------------------------------------------
        # 6. Update the YEARLY backups

        if (year := datetime.now().year) != config['last_backup']['yearly']:
            self.replace('yearly.1', 'yearly.2')
            config['last_backup']['yearly'] = year
        if month_updated:
            self.accumulate('montly.1', 'yearly.1')

        # ------------------------------------------------------------------
        # 7. Save the configuration

        with open('config.yaml', 'w') as f:
            yaml.dump(config, f)


if __name__ == '__main__':

    # Load the configuration
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Backup all directories for each remote
    for remote in config['remotes']:
        for directory, source in config['directories'].value:
            Backup(source, remote, directory).perform()
            print(f'[{datetime.now()}] "{directory}" was backed up on "{remote}"')