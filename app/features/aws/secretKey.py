import json
from typing import Any, Dict

import boto3
from botocore.exceptions import NoCredentialsError

from app.config import env_variables

settings = env_variables()


session = boto3.Session(profile_name=settings.get("PROFILE_NAME"))

secrets_client = session.client(
    "secretsmanager", region_name=settings.get("AWS_REGION_NAME")
)

secretKeys = None


def get_secret_keys() -> Dict[Any, Any]:
    global secretKeys
    if secretKeys is None:
        try:
            response = secrets_client.get_secret_value(
                SecretId=settings.get("SECRET_ID")
            )
            json_data = response["SecretString"]
            secretKeys = json.loads(json_data)
        except NoCredentialsError as e:
            print(e, "get_secret_keys")
        except Exception as e:
            print(e, "get_secret_keys")
    return secretKeys or {}
