import yaml
import subprocess
import logging as log
from os.path import join
from datetime import datetime as dt
from rclone_python import rclone


with open('config.yaml', 'r') as f:
    HOURS = yaml.safe_load(f)['daily_backup_hours']


def get_hourly_dir(hour: str) -> str:
    if hour == '00': 
        return 'hourly.24'
    elif hour in HOURS:
        return 'hourly.' + hour
    else: 
        return None


class LastSnapBackData:

    def __init__(self, file: str = 'last_snapback.yaml'):
        self.job_name = None
        self.dir_name = None
        try:
            with open(file, 'r') as f:
                self.data = yaml.safe_load(f)
                if self.data is None: self.data = {}
        except FileNotFoundError:
            log.exception('No configuration file found')
        except yaml.YAMLError:
            log.exception('Error parsing the configuration file config.yaml')

    def reset_dir(self, dir_name: str):
        if self.job_name is None: 
            log.error('No job selected')
            return

        self.data[self.job_name][dir_name] = {
            'day': 0, 'month': 'None', 'week': 0, 'year': 0,
            'failing_point': None, 'success': False
        }
        with open('last_snapback.yaml', 'w') as f: yaml.dump(self.data, f)
        return self

    def select_job(self, job_name: str):

        # Create a new job if it doesn't exist
        if job_name not in self.data.keys(): 
            self.data[job_name] = {}

        self.job_name = job_name
        return self

    def select_dir(self, dir_name: str): 

        # Check if a job has been selected
        if self.job_name is None: 
            log.error('No job selected')
            return
        
        # Create a new directory if it doesn't exist
        if dir_name not in self.data[self.job_name].keys(): 
            self.reset_dir(dir_name)

        self.dir_name = dir_name
        return self
    
    def __setitem__(self, key, value):
        if self.job_name is None or self.dir_name is None:
            log.error('No job or directory selected')
        self.data[self.job_name][self.dir_name][key] = value
        with open('last_snapback.yaml', 'w') as f: yaml.dump(self.data, f)
   
    def __getitem__(self, key):
        if self.job_name is None or self.dir_name is None:
            log.error('No job or directory selected')
        return self.data[self.job_name][self.dir_name][key]


class SnapBackJob:

    def __init__(self, 
        job_name: str, 
        job_data: dict, 
        last_snapback_data: LastSnapBackData
    ):
        self.job_data = job_data
        last_snapback_data.select_job(job_name)
        self.last_snapback_data = last_snapback_data

    def perform(self, hour: str):
        for dir_name, source in self.job_data['directories'].items():

            self.last_snapback_data.select_dir(dir_name)

            if type(source) == dict:
                sour_path = source['path']
                exclude = source['exclude']
            else:
                sour_path = source
                exclude = []

            SnapBackUpdate(
                sour_path=sour_path,
                dest_path=self.job_data['destination'],
                dir_name=dir_name,
                last_snapback_data=self.last_snapback_data,
                exclude=exclude
            ).perform_update(hour)

        log.info(f'Completed successfully')


class SnapBackUpdate:
    
    def __init__(self,
        sour_path: str,
        dest_path: str,
        dir_name: str,
        last_snapback_data: LastSnapBackData,
        exclude: list = []
    ):
        self.sour_path = sour_path
        self.dest_path = join(dest_path, dir_name)
        self.backup_dir = join(dest_path, '.snapbacks', dir_name)
        self.exclude = exclude
        last_snapback_data.select_dir(dir_name)
        self.last_snapback_data = last_snapback_data

    def _ensure_dir_exists(self, dir: str):
        '''
        Ensure that the directory exists, if not create it
        '''
        result = subprocess.run(['rclone', 'mkdir', dir])
        if result.returncode:
            log.error(f'Error creating directory {dir}')

    def _sync(self):
        '''
        Sync the source directory with the destination directory
        '''
        self._ensure_dir_exists(temp_dir := join(self.backup_dir, '.temp'))

        args = ['--fast-list', '--links', f'--backup-dir {temp_dir}']
        args.extend([f'--exclude {x}' for x in self.exclude])
        
        try: rclone.sync(self.sour_path, self.dest_path, args=args)
        except: log.exception(f'Error syncing {self.sour_path} to destination')

    def _copy(self, a: str, b: str):
        '''
        Copy the contents of directory a into directory b
        '''
        self._ensure_dir_exists(in_path := join(self.backup_dir, a))
        try: rclone.copy(in_path, join(self.backup_dir, b))
        except: log.exception(f'Error copying {a} to {b}')

    def _accumulate(self, a: str, b: str):
        '''
        Accumulate the contents of directory a into directory b
        ignoring existing files (i.e., only new files are copied)
        '''
        self._ensure_dir_exists(in_path := join(self.backup_dir, a))
        self._ensure_dir_exists(out_path := join(self.backup_dir, b))
        try:
            rclone.copy(in_path, out_path, args=['--ignore-existing'])
            rclone.delete(in_path)
        except:
            log.exception(f'Error accumulating {a} into {b}')
    
    def _move(self, a: str, b: str):
        '''
        Replace the contents of directory b with the contents of directory a
        '''
        self._ensure_dir_exists(in_path := join(self.backup_dir, a))
        try: rclone.move(in_path, join(self.backup_dir, b))
        except: log.exception(f'Error moving {a} to {b}')

    def perform_update(self, hour: str):
        '''
        Perfoms the complete reverse incremental backup process
        '''
        day = dt.now().day
        week = dt.now().isocalendar()[1]
        month = dt.now().strftime("%B")
        year = dt.now().year

        update_daily_backup   = day   != self.last_snapback_data['day']
        update_weely_backup   = week  != self.last_snapback_data['week']
        update_monthly_backup = month != self.last_snapback_data['month']
        update_yearly_backup  = year  != self.last_snapback_data['year']

        self._sync()

        if hourly_dir := get_hourly_dir(hour): 
            self._copy('.temp/', hourly_dir)

        if update_daily_backup:
            self._move('daily.2/', 'daily.3/')
            self._move('daily.1/', 'daily.2/')
            self.last_snapback_data['day'] = day
            log.info('Daily backup performed')
        self._accumulate('.temp/', 'daily.1/')

        if update_weely_backup:
            self._move('weekly.1/', 'weekly.2/')
            self.last_snapback_data['week'] = week
            log.info('Weekly backup performed')
        if update_daily_backup:
            self._accumulate('daily.1/', 'weekly.1/')

        if update_monthly_backup:
            self._move('monthly.2/', 'monthly.3/')
            self._move('monthly.1/', 'monthly.2/')
            self.last_snapback_data['month'] = month
            log.info('Monthly backup performed')
        if update_weely_backup:
            self._accumulate('weekly.1/', 'monthly.1/')

        if update_yearly_backup:
            self._move('yearly.1/', 'yearly.2/')
            self.last_snapback_data['year'] = year
            log.info('Yearly backup performed')
        if update_monthly_backup:
            self._accumulate('monthly.1/', 'yearly.1/')

    def restore(snapback: str):
        pass