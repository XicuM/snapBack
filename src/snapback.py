import os
import yaml
import datetime
from rclone_python import rclone
from os.path import join

# TODO: Let it be in the configuration file
HOURS = ['12', '16', '20', '00']


def get_hourly_dir(hour):
    if hour == '00': 
        return 'hourly.24'
    elif hour in HOURS:
        return 'hourly.' + hour
    else: 
        return None


class SnapBack:
    
    def __init__(self, source, destination, dir_name):
        self.sour_path = source

        self.dest_path = join(destination, dir_name)
        if not os.path.exists(self.dest_path): os.makedirs(self.dest_path)

        self.backup_dir = join(destination, '.snapbacks', dir_name)
        if not os.path.exists(self.backup_dir): os.makedirs(self.backup_dir)
        
        with open('config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)

    def save_config(self):
        with open('config.yaml', 'w') as f: yaml.dump(self.config, f)

    def sync(self):
        '''
        Sync the source directory with the destination directory
        '''
        rclone.sync(
            self.sour_path, 
            self.dest_path,
            args=[
                '--fast-list', 
                '--links',
                f'--backup-dir {join(self.backup_dir,".temp")}'
            ]
        )

    def copy(self, a, b):
        '''
        Copy the contents of directory a into directory b
        '''
        rclone.copy(join(self.backup_dir, a), join(self.backup_dir, b))

    def accumulate(self, a, b):
        '''
        Accumulate the contents of directory a into directory b
        ignoring existing files (i.e., only new files are copied)
        '''
        rclone.copy(
            in_path := join(self.backup_dir, a), 
            join(self.backup_dir, b),
            args=['--ignore-existing']
        )
        rclone.delete(in_path)
    
    def move(self, a, b):
        '''
        Replace the contents of directory b with the contents of directory a
        '''
        rclone.move(join(self.backup_dir, a), join(self.backup_dir, b))

    def update(self, hour):
        '''
        Description here
        '''

        # --------------------------------------------------------------
        # 0. Get data

        # TODO: This can lead to data loss
        day = datetime.now().weekday()
        week = datetime.now().isocalendar()[1]
        month = datetime.now().strftime("%B")
        year = datetime.now().year

        update_daily_backup = day!=self.config['last_backup']['daily']
        update_weely_backup = week!=self.config['last_backup']['weekly']
        update_monthly_backup = month!=self.config['last_backup']['monthly']
        update_yearly_backup = year!=self.config['last_backup']['yearly']

        # --------------------------------------------------------------
        # 1. Sync destination with source and save the incremental output in .temp
        self.sync()

        # --------------------------------------------------------------
        # 2. Save the backup in the hourly backup
        
        if hourly_dir := get_hourly_dir(hour):
            self.copy('.temp', hourly_dir)

        # --------------------------------------------------------------
        # 3. Update the DAILY backups

        if update_daily_backup:
            self.move('daily.2', 'daily.3')
            self.move('daily.1', 'daily.2')
            self.config['last_backup']['daily'] = day
            self.save_config()
        self.accumulate('.temp', 'daily.1')

        # --------------------------------------------------------------
        # 4. Update the WEEKLY backups

        if update_weely_backup:
            self.move('weekly.1', 'weekly.2')
            self.config['last_backup']['weekly'] = week
            self.save_config()
        if update_daily_backup:
            self.accumulate('daily.1', 'weekly.1')

        # --------------------------------------------------------------
        # 5. Update the MONTHLY backups

        if update_monthly_backup:
            self.move('monthly.2', 'monthly.3')
            self.move('monthly.1', 'monthly.2')
            self.config['last_backup']['monthly'] = month
            self.save_config()
        if update_weely_backup:
            self.accumulate('weekly.1', 'monthly.1')

        # --------------------------------------------------------------
        # 6. Update the YEARLY backups

        if update_yearly_backup:
            self.move('yearly.1', 'yearly.2')
            self.config['last_backup']['yearly'] = year
            self.save_config()
        if update_monthly_backup:
            self.accumulate('montly.1', 'yearly.1')


    def restore(snapback):
        pass