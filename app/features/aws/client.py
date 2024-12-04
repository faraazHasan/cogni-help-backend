from contextlib import AsyncExitStack
from typing import TYPE_CHECKING

import boto3

from app.features.aws.secretKey import get_secret_keys

keys = get_secret_keys()

__all__ = ("get_client",)

if TYPE_CHECKING:
    pass


async def get_client(exit_stack: AsyncExitStack, service: str = "s3"):
    session = boto3.Session()
    DEBUG = True
    if DEBUG:
        session = boto3.Session()

    return await exit_stack.enter_async_context(
        session.client(
            service,
            aws_access_key_id=keys["AWS_ACCESS_KEY"],
            aws_secret_access_key=keys["AWS_SECRET_KEY"],
            region_name=keys["AWS_REGION_NAME"],
            config=boto3.session.Config(signature_version="s3v4"),
        )
    )
