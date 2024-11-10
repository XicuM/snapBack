import yaml
import argparse
import logging as log
from datetime import datetime
from snapback import SnapBack


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

    # Create the argument parser
    args = command_parser()

    # Set the logging configuration
    log.basicConfig(
        level=getattr(log, args.log_level),
        filename='snapback.log',
        filemode='a',
        format='%(asctime)s [%(levelname)s] %(message)s'
    )

    # Backup all directories for each remote
    for remote in config['remotes'].values():
        for directory, source in config['directories'].keys():
            SnapBack(source, remote, directory).update(
                hour=str(datetime.now().hour).zfill(2)
            )
            print(f'[{datetime.now()}] "{directory}" was backed up on "{remote}"')


if __name__ == '__main__':
    main()