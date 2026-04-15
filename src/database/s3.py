import asyncio
import os
from contextlib import asynccontextmanager
from aiobotocore.session import get_session
import dotenv
from fastapi import UploadFile
import json

dotenv.load_dotenv()

class S3Client:
    def __init__(
            self,
            access_key: str,
            secret_key:str,
            endpoint_url:str,
            bucket_name:str,
    ):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url
        }
        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client(service_name = 's3', **self.config) as client:
            yield client

    @asynccontextmanager
    async def get_streaming_object(self, object_name: str):
        async with self.get_client() as client:
            response = await client.get_object(Bucket=self.bucket_name, Key=object_name)
            yield response

    async def get_all_objects(
            self,
    ):
        async with self.get_client() as client:
            result = await client.list_objects(
                Bucket=self.bucket_name
                )
        return result['Contents']

    async def get_object(
            self,
            object_name: str
    ):
        async with self.get_client() as client:
            result = await client.get_object(
                Bucket=self.bucket_name,
                Key = object_name
            )
            return await result['Body'].read()

    async def upload_object(
            self,
            file: UploadFile,
    ):
        async with self.get_client() as client:
            await client.put_object(
                Bucket=self.bucket_name,
                Key=file.filename,
                Body=file.file
            )

    async def delete_object(
            self,
            object_name: str,
    ):
        async with self.get_client() as client:
            await client.delete_object(
                Bucket=self.bucket_name,
                Key=object_name
            )




def get_s3_client():
    s3_photo = S3Client(
        access_key=os.environ["AWS_ACCESS_KEY_ID"],
        secret_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        endpoint_url=os.environ["AWS_ENDPOINT_URL"],
        bucket_name="test-bucket",
    )
    return s3_photo