import yaml
import argparse
import logging as log
from snapback import SnapBack


def command_parser(config: dict) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="snapBack restore")
    parser.add_argument('remote', 
        type=str,
        choices=config['remotes'].keys(), 
        help='Remote alias'
    )
    parser.add_argument('directory',
        type=str,
        choices=config['directories'].keys(),
        help='Directory to restore'
    )
    parser.add_argument('snapback', 
        type=str, 
        choices=['hourly.12', 'hourly.16', 'hourly.20', 'hourly.24', 
                 'daily.1', 'daily.2', 'daily.3', 'weekly.1', 'weekly.2', 
                 'monthly.1', 'monthly.2', 'monthly.3', 'yearly.1', 'yearly.2'],
        help='Snapback to restore'
    )
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
    args = command_parser(config)
    
    # Set the logging configuration
    log.basicConfig(
        level=getattr(log, args.log_level),
        filename='snapback.log',
        filemode='a',
        format='%(asctime)s Restore: [%(levelname)s] %(message)s'
    )

    SnapBack(
        config['directories'][args.directory], 
        config['remotes'][args.remote],
        args.directory
    ).restore()
    

if __name__ == '__main__':
    main()