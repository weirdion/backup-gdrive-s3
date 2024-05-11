import argparse
import os

import boto3

from rclone_config import GDriveToken, RCloneConfig
from secret_manager import get_secrets, update_secrets


def _init_secrets_manager_client():
    # Initialize the AWS Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name="us-east-1")
    return client


def setup():
    # Retrieve credentials from AWS Secrets Manager
    secrets_manager = _init_secrets_manager_client()
    secrets_dict = get_secrets(secrets_manager, os.environ["SECRET_NAME"])

    # Write credentials to an INI file
    rclone_config = RCloneConfig()
    # load from file or get default values
    rclone_config.load_from_file()

    # inject secrets into the config
    rclone_config.update_gdrive_token(GDriveToken(**secrets_dict))

    # save to .rclone.conf
    rclone_config.save_to_file()


def clean():
    # Write credentials to an INI file
    rclone_config = RCloneConfig()
    # load from file, rclone refreshes the token during the run
    rclone_config.load_from_file()

    # Retrieve credentials from AWS Secrets Manager
    secrets_manager = _init_secrets_manager_client()
    update_secrets(secrets_manager, os.environ["SECRET_NAME"], rclone_config.gdrive["token"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage app token")
    parser.add_argument("choice", nargs="?", choices=["setup", "clean"], default=None)
    args = parser.parse_args()

    if args.choice == "setup":
        setup()
    elif args.choice == "clean":
        clean()
    else:
        print("Please provide a choice: 'setup' or 'clean'.")
