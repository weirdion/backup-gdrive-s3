import json
import os
from configparser import ConfigParser
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict


@dataclass
class GDriveToken:
    access_token: str = ""
    token_type: str = "Bearer"
    refresh_token: str = ""
    expiry: str = ""  # Keeping this as string since rclone manages the date


@dataclass
class RCloneConfig:
    region: str = "us-east-1"
    storage_class: str = "GLACIER_IR"
    aws_s3: Dict[str, str] = field(init=False)
    gdrive: Dict[str, str] = field(init=False)
    file_path: Path = field(init=False, default=Path(".rclone.conf"))

    def __post_init__(self):
        self.aws_s3 = {
            "type": "s3",
            "provider": "AWS",
            "region": self.region,
            "env_auth": True,
            "acl": "private",
            "storage_class": self.storage_class,
            "bucket_acl": "private",
            "sse_customer_algorithm": "",
        }
        self.gdrive = {
            "type": "drive",
            "scope": "drive.readonly",
            "token": asdict(GDriveToken()),
            "team_drive": "",
        }

    def load_from_file(self):
        if self.file_path.exists():
            config = ConfigParser()
            config.read(self.file_path)

            self.aws_s3 = {
                "type": config.get("AWSS3", "type", fallback=self.aws_s3["type"]),
                "provider": config.get("AWSS3", "provider", fallback=self.aws_s3["provider"]),
                "region": config.get("AWSS3", "region", fallback=self.aws_s3["region"]),
                "env_auth": config.getboolean(
                    "AWSS3", "env_auth", fallback=self.aws_s3["env_auth"]
                ),
                "acl": config.get("AWSS3", "acl", fallback=self.aws_s3["acl"]),
                "storage_class": config.get(
                    "AWSS3", "storage_class", fallback=self.aws_s3["storage_class"]
                ),
                "bucket_acl": config.get("AWSS3", "bucket_acl", fallback=self.aws_s3["bucket_acl"]),
                "sse_customer_algorithm": config.get(
                    "AWSS3",
                    "sse_customer_algorithm",
                    fallback=self.aws_s3["sse_customer_algorithm"],
                ),
            }

            self.gdrive = {
                "type": config.get("GDrive", "type", fallback=self.gdrive["type"]),
                "scope": config.get("GDrive", "scope", fallback=self.gdrive["scope"]),
                "token": config.get("GDrive", "token", fallback=self.gdrive["token"]),
                "team_drive": config.get(
                    "GDrive", "team_drive", fallback=self.gdrive["team_drive"]
                ),
            }

    def save_to_file(self):
        config = ConfigParser()
        config.add_section("AWSS3")
        config.set("AWSS3", "type", self.aws_s3["type"])
        config.set("AWSS3", "provider", self.aws_s3["provider"])
        config.set("AWSS3", "region", self.aws_s3["region"])
        config.set("AWSS3", "env_auth", str(self.aws_s3["env_auth"]))
        config.set("AWSS3", "acl", self.aws_s3["acl"])
        config.set("AWSS3", "storage_class", self.aws_s3["storage_class"])
        config.set("AWSS3", "bucket_acl", self.aws_s3["bucket_acl"])
        config.set("AWSS3", "sse_customer_algorithm", self.aws_s3["sse_customer_algorithm"])

        config.add_section("GDrive")
        config.set("GDrive", "type", self.gdrive["type"])
        config.set("GDrive", "scope", self.gdrive["scope"])
        config.set("GDrive", "token", json.dumps(self.gdrive["token"]))
        config.set("GDrive", "team_drive", self.gdrive["team_drive"])

        with self.file_path.open("w", encoding="utf-8") as f:
            config.write(f)

    def delete_config_file(self):
        # delete file_path
        if self.file_path.exists():
            os.remove(self.file_path)
            print(f"Config file '{self.file_path}' deleted.")

    def update_gdrive_token(self, new_token: GDriveToken):
        self.gdrive["token"] = asdict(new_token)
