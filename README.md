Backup scripts for syncing Google Drive to S3 Glacier IR
---

This project uses [rclone](https://github.com/rclone/rclone) for all sync operations, with some python scripts to set up configuration and access.

The sync operation is run with github workflow on a schedule.

## Setting up

### RSync - Google Drive

RSync Google Drive documentation - [link](https://rclone.org/drive/).

We are only reading from Google Drive, so we only need `drive.readonly`.

Once we run `rclone config` for Google Drive, the output is in the format

```toml
[GDrive]
type = drive
scope = drive.readonly
token = {"access_token":"ABCD","token_type":"Bearer","refresh_token":"XYZ","expiry":"2024-05-24T13:57:58.955387075Z"}
```

The token is stored as key-value pairs in AWS Secrets Manager, retrieved during runtime and updated in-place.

### AWS

AWS is used to archive all the documents from Google Drive. There are three components we need to set up:

#### 1. Secrets Manager

The Google Drive token is stored as key-value pairs in Secrets Manager. The name of the secret is stored in GH Actions as a secret - `SECRET_NAME`.

[Secrets Manager Pricing](https://aws.amazon.com/secrets-manager/pricing/) : $0.40/month + $0.05 per 10,000 API Calls = $0.45/month

#### 2. S3 Bucket

A private S3 Bucket is used to archive all the documents. The configuration uses (Glacier Instant Retrieval)[https://aws.amazon.com/s3/storage-classes/glacier/instant-retrieval/],
with the assumption that the data is largely for cold storage but might be needed at a moment's notice.

[S3 Pricing](https://aws.amazon.com/s3/pricing/?nc=sn&loc=4):

Storage
 - Storage Costs: $0.004 per GB
 - Data Transfer IN from internet: $0.00 per GB
 - PUT request: $0.02 per 1000 requests

Retrieval
 - Data Transfer OUT to internet: $0.09 per GB
 - GET request: $0.01 per 1000 requests
 - Data retrieval: $0.03 per GB

#### 3. IAM Role

We need a role that is able to read and write to the S3 bucket we are using, for syncing,
and, be able to read and write to the Secrets Manager secret to retrieve and update the Google Drive token.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:DeleteObject",
                "s3:GetObject",
                "s3:PutObject",
                "s3:PutObjectAcl"
            ],
            "Resource": [
                "arn:aws:s3:::my-backup-bucket/*",
                "arn:aws:s3:::my-backup-bucket"
            ]
        },
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret",
                "secretsmanager:PutSecretValue",
                "secretsmanager:UpdateSecretVersionStage",
                "secretsmanager:ListSecretVersionIds",
                "secretsmanager:UpdateSecret"
            ],
            "Resource": "arn:aws:secretsmanager:us-east-1:012345679:secret:MY-SECRET"
        }
    ]
}
```
