import json

import boto3
from botocore.exceptions import ClientError


def get_secrets(client: boto3.Session, secret_name: str) -> dict:
    """
    Function that gets the value of a secret.

    :return: The value of the secret. When the secret is a string, the value is
            contained in the `SecretString` field. When the secret is bytes,
            it is contained in the `SecretBinary` field.
    """
    try:
        kwargs = {"SecretId": secret_name}
        response = client.get_secret_value(**kwargs)
    except ClientError:
        print(f"Couldn't get value for secret.")
        raise
    else:
        return json.loads(response["SecretString"])


def update_secrets(client, secret_name, gdrive_token):
    """
    Function that gets the value of a secret.

    :return: The value of the secret. When the secret is a string, the value is
            contained in the `SecretString` field. When the secret is bytes,
            it is contained in the `SecretBinary` field.
    """
    try:
        kwargs = {
            "SecretId": secret_name,
            "SecretString": (
                gdrive_token if isinstance(gdrive_token, str) else json.dumps(gdrive_token)
            ),
        }
        response = client.update_secret(**kwargs)
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            print(f"Successfully updated value for secret.")
        else:
            print(f"Something went wrong while updating the secret: {response}")
    except ClientError:
        print(f"Couldn't get value for secret.")
        raise
