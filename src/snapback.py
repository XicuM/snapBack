import os
import yaml
import logging as log
from datetime import datetime as dt
from rclone_python import rclone
from os.path import join

with open('config.yaml', 'r') as f:
    HOURS = yaml.safe_load(f)['daily_backup_hours']


def get_hourly_dir(hour: str) -> str:
    if hour == '00': 
        return 'hourly.24'
    elif hour in HOURS:
        return 'hourly.' + hour
    else: 
        return None


def ensure_dir_exists(dir: str):
    if not os.path.exists(dir): os.makedirs(dir)

class SnapBack:
    
    def __init__(self,  
        source: str, 
        destination: str, 
        dir_name: str, 
        config: dict = None
    ):
        self.sour_path = source
        self.dest_path = join(destination, dir_name)
        self.backup_dir = join(destination, '.snapbacks', dir_name)

        ensure_dir_exists(self.dest_path)
        ensure_dir_exists(self.backup_dir)

        if config:
            self.config = config
        else:
            try:
                with open('config.yaml', 'r') as f:
                    self.config = yaml.safe_load(f)
            except FileNotFoundError:
                log.exception('No configuration file found')
            except yaml.YAMLError:
                log.exception('Error parsing the configuration file config.yaml')

    def save_config(self):
        with open('config.yaml', 'w') as f: yaml.dump(self.config, f)

    def sync(self):
        '''
        Sync the source directory with the destination directory
        '''
        ensure_dir_exists(temp_dir := join(self.backup_dir,".temp"))
        try:
            rclone.sync(
                self.sour_path, 
                self.dest_path,
                args=[
                    '--fast-list', 
                    '--links',
                    f'--backup-dir {temp_dir}'
                ]
            )
        except:
            log.exception(f'Error syncing {self.sour_path} to destination')

    def copy(self, a: str, b: str):
        '''
        Copy the contents of directory a into directory b
        '''
        ensure_dir_exists(in_path := join(self.backup_dir, a))
        try: rclone.copy(in_path, join(self.backup_dir, b))
        except: log.exception(f'Error copying {a} to {b}')

    def accumulate(self, a: str, b: str):
        '''
        Accumulate the contents of directory a into directory b
        ignoring existing files (i.e., only new files are copied)
        '''
        ensure_dir_exists(in_path := join(self.backup_dir, a))
        ensure_dir_exists(out_path := join(self.backup_dir, b))
        try:
            rclone.copy(in_path, out_path, args=['--ignore-existing'])
            rclone.delete(in_path)
        except:
            log.exception(f'Error accumulating {a} into {b}')
    
    def move(self, a: str, b: str):
        '''
        Replace the contents of directory b with the contents of directory a
        '''
        ensure_dir_exists(in_path := join(self.backup_dir, a))
        try: rclone.move(in_path, join(self.backup_dir, b))
        except: log.exception(f'Error moving {a} to {b}')

    def update(self, hour: str, updates: dict = None):
        '''
        Description here
        '''

        # --------------------------------------------------------------
        # 0. See what needs to be updated

        day = dt.now().weekday()
        week = dt.now().isocalendar()[1]
        month = dt.now().strftime("%B")
        year = dt.now().year

        if updates:
            update_daily_backup   = updates['daily']
            update_weely_backup   = updates['weekly']
            update_monthly_backup = updates['monthly']
            update_yearly_backup  = updates['yearly']
        else:
            update_daily_backup   = day   != self.config['last_backup']['daily']
            update_weely_backup   = week  != self.config['last_backup']['weekly']
            update_monthly_backup = month != self.config['last_backup']['monthly']
            update_yearly_backup  = year  != self.config['last_backup']['yearly']

        # --------------------------------------------------------------
        # 1. Sync destination with source and save the incremental output in .temp
        self.sync()

        # --------------------------------------------------------------
        # 2. Save the backup in the hourly backup
        
        if hourly_dir := get_hourly_dir(hour):
            self.copy('.temp/', hourly_dir)

        # --------------------------------------------------------------
        # 3. Update the DAILY backups

        if update_daily_backup:
            self.move('daily.2/', 'daily.3/')
            self.move('daily.1/', 'daily.2/')
            self.config['last_backup']['daily'] = day
            #self.save_config()
        self.accumulate('.temp/', 'daily.1/')

        # --------------------------------------------------------------
        # 4. Update the WEEKLY backups

        if update_weely_backup:
            self.move('weekly.1/', 'weekly.2/')
            self.config['last_backup']['weekly'] = week
            #self.save_config()
        if update_daily_backup:
            self.accumulate('daily.1/', 'weekly.1/')

        # --------------------------------------------------------------
        # 5. Update the MONTHLY backups

        if update_monthly_backup:
            self.move('monthly.2/', 'monthly.3/')
            self.move('monthly.1/', 'monthly.2/')
            self.config['last_backup']['monthly'] = month
            #self.save_config()
        if update_weely_backup:
            self.accumulate('weekly.1/', 'monthly.1/')

        # --------------------------------------------------------------
        # 6. Update the YEARLY backups

        if update_yearly_backup:
            self.move('yearly.1/', 'yearly.2/')
            self.config['last_backup']['yearly'] = year
            #self.save_config()
        if update_monthly_backup:
            self.accumulate('monthly.1/', 'yearly.1/')


    def restore(snapback: str):
        pass