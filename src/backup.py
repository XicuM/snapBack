import os
import yaml
import argparse
import logging as log
from datetime import datetime
from snapback import SnapBackJob, LastSnapBackData


def command_parser():

    parser = argparse.ArgumentParser(description="snapBack backup")

    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='ERROR',
        help='Set the logging level (default: ERROR)'
    )
    
    return parser.parse_args()


def main():
    # Load the configuration
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Create data file if it doesn't exist
    if not os.path.exists('last_snapback.yaml'):
        with open('last_snapback.yaml', 'w') as f:
            yaml.dump({
                'day': 0, 'month': 'None', 'week': 0, 'year': 0,
                'failing_point': None, 'success': False
            }, f)

    # Create the argument parser
    args = command_parser()

    # Set the logging configuration
    log.basicConfig(
        level=getattr(log, args.log_level),
        filename='snapback.log',
        filemode='a',
        format='%(asctime)s [%(levelname)s] %(message)s'
    )

    last_snapback_data = LastSnapBackData()

    for job_name, job_data in config['jobs'].items():
        SnapBackJob(job_name, job_data, last_snapback_data).perform(
            hour=str(datetime.now().hour).zfill(2)
        )

    log.info('All jobs completed successfully')


if __name__ == '__main__':
    main()