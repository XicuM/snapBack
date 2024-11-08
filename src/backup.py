import yaml
from datetime import datetime
from snapback import SnapBack


def main():
    # Load the configuration
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Backup all directories for each remote
    for remote in config['remotes'].values():
        for directory, source in config['directories'].keys():
            SnapBack(source, remote, directory).update(
                hour=str(datetime.now().hour).zfill(2)
            )
            print(f'[{datetime.now()}] "{directory}" was backed up on "{remote}"')


if __name__ == '__main__':
    main()