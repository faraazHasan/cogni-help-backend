from typing import List

import boto3
from botocore.exceptions import ClientError
from fastapi import FastAPI

from app.common import constants
from app.config import env_variables
from app.features.aws.secretKey import get_secret_keys

app = FastAPI()
settings = env_variables()
keys = get_secret_keys()


s3_client = boto3.client(
    "s3",
    aws_access_key_id=keys["AWS_ACCESS_KEY"],
    aws_secret_access_key=keys["AWS_SECRET_KEY"],
    region_name=keys["AWS_REGION_NAME"],
    config=boto3.session.Config(signature_version="v4"),
)


# Generate presignedUrl
async def generate_presigned_urls(file_path: str) -> List[dict]:
    try:
        bucket_name = keys["AWS_BUCKET"]
        presigned_url = s3_client.generate_presigned_url(
            "put_object",
            Params={"Bucket": bucket_name, "Key": file_path},
            ExpiresIn=3600,
        )
        return {
            "message": constants.URL_GENERATED_SUCCESSFULLY,
            "success": True,
            "data": {"filename": file_path, "presigned_url": presigned_url},
        }

    except ClientError as e:
        print(e)
        return {
            "message": constants.SOMETHING_WENT_WRONG,
            "success": False,
        }
