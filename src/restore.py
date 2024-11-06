import yaml
import argparse
from datetime import datetime
from snapback import SnapBack

def main():
    # Load the configuration
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Create the argument parser
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
    
    args = parser.parse_args()
    SnapBack(
        config['directories'][args.directory], 
        config['remotes'][args.remote],
        args.directory
    ).restore()
    

if __name__ == '__main__':
    main()